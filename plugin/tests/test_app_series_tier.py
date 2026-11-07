"""Series Tier Overrides through the facade, over the fake ports."""

import pytest
from fakes import FakeLibrary, FakePrefs

from tierlist.app import TIER_CONFIG_KEY, TierList
from tierlist.series_tiers import SERIES_TIER_OVERRIDES_KEY
from tierlist.tiers import Tier, TierConfig

CONFIG = TierConfig(tiers=(Tier('s', 'S', '#ff7f7f'), Tier('a', 'A', '#ffbf7f')))


def facade() -> tuple[TierList, FakeLibrary, FakePrefs]:
    library = FakeLibrary()
    prefs = FakePrefs({TIER_CONFIG_KEY: CONFIG.to_dict()})
    return TierList(library, prefs), library, prefs


def shelve(library: FakeLibrary, members: dict[int, str]) -> None:
    """Put these books on a series shelf, by book id."""
    library.values['series'] = dict(members)


def test_set_series_tier_stores_an_override_for_each_distinct_series() -> None:
    app, library, prefs = facade()
    shelve(library, {1: 'Dune', 2: 'Dune', 3: 'Earthsea'})
    app.set_series_tier([1, 2, 3], 's')
    assert app.series_tier_overrides() == {'Dune': 's', 'Earthsea': 's'}
    assert prefs.data[SERIES_TIER_OVERRIDES_KEY] == {'Dune': 's', 'Earthsea': 's'}


def test_set_series_tier_twice_overwrites_the_override() -> None:
    app, library, _ = facade()
    shelve(library, {1: 'Dune'})
    app.set_series_tier([1], 's')
    app.set_series_tier([1], 'a')
    assert app.series_tier_overrides() == {'Dune': 'a'}


def test_clear_series_tier_returns_only_those_series_to_auto() -> None:
    app, library, _ = facade()
    shelve(library, {1: 'Dune', 2: 'Earthsea'})
    app.set_series_tier([1, 2], 's')
    app.clear_series_tier([1])
    assert app.series_tier_overrides() == {'Earthsea': 's'}


def test_clearing_a_series_without_an_override_is_fine() -> None:
    app, library, _ = facade()
    shelve(library, {1: 'Dune'})
    app.clear_series_tier([1])
    assert app.series_tier_overrides() == {}


def test_unknown_tier_id_raises_and_stores_nothing() -> None:
    app, library, prefs = facade()
    shelve(library, {1: 'Dune'})
    with pytest.raises(ValueError):
        app.set_series_tier([1], 'z')
    assert SERIES_TIER_OVERRIDES_KEY not in prefs.data


def test_a_book_without_a_series_stores_no_override() -> None:
    app, library, _ = facade()
    shelve(library, {1: 'Dune'})
    app.set_series_tier([1, 2], 's')
    assert app.series_tier_overrides() == {'Dune': 's'}


def test_a_renamed_series_leaves_its_override_orphaned() -> None:
    app, library, _ = facade()
    shelve(library, {1: 'Dune'})
    app.set_series_tier([1], 's')
    shelve(library, {1: 'Dune Messiah'})
    assert app.series_tier_orphans() == ['Dune']


def test_an_override_for_a_series_still_in_the_library_is_not_orphaned() -> None:
    app, library, _ = facade()
    shelve(library, {1: 'Dune', 2: 'Earthsea'})
    app.set_series_tier([1, 2], 's')
    assert app.series_tier_orphans() == []


def test_corrupt_overrides_in_prefs_are_ignored() -> None:
    app, library, prefs = facade()
    shelve(library, {1: 'Dune'})
    prefs.data[SERIES_TIER_OVERRIDES_KEY] = 'not a mapping'
    assert app.series_tier_overrides() == {}
    app.set_series_tier([1], 's')
    assert app.series_tier_overrides() == {'Dune': 's'}


def test_non_string_override_entries_are_ignored() -> None:
    app, _, prefs = facade()
    prefs.data[SERIES_TIER_OVERRIDES_KEY] = {'Dune': 's', 'Earthsea': None, 7: 's', 'Foundation': ''}
    assert app.series_tier_overrides() == {'Dune': 's'}

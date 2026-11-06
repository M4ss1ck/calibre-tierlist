"""Send to Tier and Clear tier through the facade, over the fake ports."""

from collections.abc import Iterable

import pytest
from fakes import FakeLibrary, FakePrefs

from tierlist.app import TIER_COLUMN_OFFERED_KEY, TIER_CONFIG_KEY, TierList
from tierlist.tiers import DEFAULT_TIER_CONFIG, Tier, TierConfig

CUSTOM = TierConfig(tiers=(Tier('s', 'S-Tier', '#ff7f7f'), Tier('a', 'A-Tier', '#ffbf7f')))


def facade(
    config: TierConfig | None = None, columns: Iterable[str] = ('#tier',)
) -> tuple[TierList, FakeLibrary, FakePrefs]:
    library = FakeLibrary(columns)
    prefs = FakePrefs({} if config is None else {TIER_CONFIG_KEY: config.to_dict()})
    return TierList(library, prefs), library, prefs


def test_set_book_tier_stores_the_tier_id_not_the_label() -> None:
    app, library, _ = facade(CUSTOM)
    app.set_book_tier([1], 's')
    assert library.values['#tier'] == {1: 's'}


def test_set_book_tier_writes_a_multi_book_selection_in_one_write() -> None:
    app, library, _ = facade()
    app.set_book_tier([1, 2, 3], 'b')
    assert library.values['#tier'] == {1: 'b', 2: 'b', 3: 'b'}
    assert library.writes == 1


def test_clear_book_tier_removes_values() -> None:
    app, library, _ = facade()
    app.set_book_tier([1, 2], 'b')
    app.clear_book_tier([2])
    assert library.values['#tier'] == {1: 'b'}
    assert library.writes == 2


def test_clear_book_tier_on_an_untiered_book_is_fine() -> None:
    app, library, _ = facade()
    app.clear_book_tier([7])
    assert library.values['#tier'] == {}
    assert library.writes == 1


def test_unknown_tier_id_raises_and_writes_nothing() -> None:
    app, library, _ = facade()
    with pytest.raises(ValueError):
        app.set_book_tier([1], 'z')
    assert library.writes == 0


def test_tier_config_falls_back_to_the_default() -> None:
    app, _, _ = facade()
    assert app.tier_config() == DEFAULT_TIER_CONFIG


def test_tier_config_honours_a_stored_config() -> None:
    app, _, _ = facade(CUSTOM)
    assert app.tier_config() == CUSTOM


def test_tier_column_ready_true_and_false() -> None:
    app, _, _ = facade()
    missing, _, _ = facade(columns=())
    assert app.tier_column_ready()
    assert not missing.tier_column_ready()


def test_tier_column_ready_honours_a_stored_custom_column() -> None:
    config = TierConfig(tiers=DEFAULT_TIER_CONFIG.tiers, tier_column='#rank')
    ready, _, _ = facade(config, columns=('#rank',))
    stale, _, _ = facade(config, columns=('#tier',))
    assert ready.tier_column_ready()
    assert not stale.tier_column_ready()


def test_tier_column_offer_defaults_to_not_offered() -> None:
    app, _, _ = facade()
    assert not app.tier_column_offered()


def test_mark_tier_column_offered_records_the_offer() -> None:
    app, _, prefs = facade()
    app.mark_tier_column_offered()
    assert app.tier_column_offered()
    assert prefs.data[TIER_COLUMN_OFFERED_KEY] is True


def test_empty_selection_writes_nothing() -> None:
    app, library, _ = facade()
    app.set_book_tier([], 's')
    app.clear_book_tier([])
    assert library.writes == 0

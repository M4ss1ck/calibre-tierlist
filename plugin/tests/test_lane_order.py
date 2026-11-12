"""Lane Order prefs: what is stored, and pruning places that name nothing current."""

from fakes import FakeLibrary, FakePrefs, FakeSavedSearches

from tierlist.config_admin import ConfigAdmin
from tierlist.lane_order import (
    LANE_ORDER_KEY,
    UNRANKED_LANE,
    load_order,
    place_for,
    place_from_dict,
    place_to_dict,
    prune,
    save_order,
)
from tierlist.tiers import DEFAULT_TIER_CONFIG


def test_a_place_is_built_and_stored_in_either_shape() -> None:
    assert place_for('series', 'Dune') == ('series', 'Dune')
    assert place_for('book', 7) == ('book', 7)
    assert place_to_dict(('book', 7)) == {'book': 7}
    assert place_from_dict({'series': 'Dune'}) == ('series', 'Dune')


def test_save_and_load_round_trip_each_place() -> None:
    prefs = FakePrefs()

    save_order(prefs, {'s': [('series', 'Dune'), ('book', 7)], UNRANKED_LANE: [('book', 3)]})

    assert prefs.data[LANE_ORDER_KEY] == {
        's': [{'series': 'Dune'}, {'book': 7}],
        UNRANKED_LANE: [{'book': 3}],
    }
    assert load_order(prefs) == {'s': [('series', 'Dune'), ('book', 7)], UNRANKED_LANE: [('book', 3)]}


def test_load_ignores_corrupt_and_empty_places() -> None:
    prefs = FakePrefs({LANE_ORDER_KEY: {'s': [{'series': ''}, {'book': True}, {'nope': 1}, {'book': 5}, 'x'], 3: []}})

    assert load_order(prefs) == {'s': [('book', 5)]}


def test_prune_drops_stale_series_names_and_book_ids() -> None:
    prefs = FakePrefs(
        {
            LANE_ORDER_KEY: {
                's': [{'series': 'Dune'}, {'book': 1}, {'series': 'Old'}, {'book': 99}],
                UNRANKED_LANE: [{'book': 2}],
            }
        }
    )

    prune(prefs, frozenset({'Dune'}), frozenset({1}))

    assert prefs.data[LANE_ORDER_KEY] == {'s': [{'series': 'Dune'}, {'book': 1}]}


def test_prune_writes_nothing_when_no_order_is_stored() -> None:
    prefs = FakePrefs()

    prune(prefs, frozenset({'Dune'}), frozenset({1}))

    assert LANE_ORDER_KEY not in prefs.data


def test_saving_settings_prunes_stale_places() -> None:
    library = FakeLibrary()
    library.values['series'] = {1: 'Dune'}
    prefs = FakePrefs({LANE_ORDER_KEY: {'s': [{'series': 'Dune'}, {'book': 99}]}})
    admin = ConfigAdmin(library, prefs, FakeSavedSearches())

    admin.save(DEFAULT_TIER_CONFIG)

    assert prefs.data[LANE_ORDER_KEY] == {'s': [{'series': 'Dune'}]}

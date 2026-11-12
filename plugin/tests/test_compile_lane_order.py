"""Compile Lane Order: stored places first, then unplaced items by date read, undated last, then name or title."""

from datetime import UTC, date, datetime

from fakes import FakeCovers, FakeLibrary, FakePrefs

from tierlist.app import TIER_CONFIG_KEY, TierList
from tierlist.compile import CompileRequest, TierListData
from tierlist.lane_order import LANE_ORDER_KEY
from tierlist.tiers import Tier, TierConfig

NOW = datetime(2026, 11, 6, 12, 0, tzinfo=UTC)
TODAY = date(2026, 11, 6)
CONFIG = TierConfig(tiers=(Tier('s', 'S', '#ff7f7f'), Tier('a', 'A', '#ffbf7f'), Tier('b', 'B', '#ffdf7f')))


def facade(library: FakeLibrary, order: dict[str, list[dict[str, object]]] | None = None) -> TierList:
    prefs = FakePrefs({TIER_CONFIG_KEY: CONFIG.to_dict(), LANE_ORDER_KEY: order or {}})
    return TierList(library, prefs, lambda: TODAY, lambda: NOW, covers=FakeCovers())


def places(data: TierListData, tier: str) -> list[tuple[str, object]]:
    lane = next(lane for lane in data.lanes if lane.tier == tier)
    return [('series', item.stack) if item.stack is not None else ('book', item.card) for item in lane.items]


def test_stored_order_is_honoured() -> None:
    library = FakeLibrary(types={'#date_read': 'datetime'})
    library.values['title'] = {1: 'Card'}
    library.values['#tier'] = {1: 's', 2: 's'}
    library.values['series'] = {2: 'Dune'}
    library.values['series_index'] = {2: 1.0}
    app = facade(library, {'s': [{'book': 1}, {'series': 'Dune'}]})

    data = app.compile(CompileRequest('library', (1, 2), 'Lib', '0.1.0'))

    assert places(data, 's') == [('book', 1), ('series', 'Dune')]


def test_unplaced_items_are_appended_by_date_read_then_name_or_title() -> None:
    library = FakeLibrary(types={'#date_read': 'datetime'})
    library.values['title'] = {1: 'Placed', 2: 'Two', 3: 'Alpha', 4: 'Aardvark'}
    library.values['#tier'] = {1: 's', 2: 's', 3: 's', 4: 's', 5: 's'}
    library.values['#date_read'] = {1: TODAY, 2: date(2022, 1, 1), 5: date(2023, 1, 1)}
    library.values['series'] = {5: 'Dune'}
    library.values['series_index'] = {5: 1.0}
    app = facade(library, {'s': [{'book': 1}]})

    data = app.compile(CompileRequest('library', (1, 2, 3, 4, 5), 'Lib', '0.1.0'))

    assert places(data, 's') == [
        ('book', 1),
        ('book', 2),
        ('series', 'Dune'),
        ('book', 4),
        ('book', 3),
    ]


def test_a_series_whose_auto_tier_changed_lands_at_the_end_of_its_new_lane() -> None:
    library = FakeLibrary(types={'#date_read': 'datetime'})
    library.values['title'] = {1: 'Card S', 2: 'Dune One', 3: 'Card B'}
    library.values['#tier'] = {1: 's', 2: 'b', 3: 'b'}
    library.values['series'] = {2: 'Dune'}
    library.values['series_index'] = {2: 1.0}
    app = facade(library, {'s': [{'book': 1}, {'series': 'Dune'}], 'b': [{'book': 3}]})

    data = app.compile(CompileRequest('library', (1, 2, 3), 'Lib', '0.1.0'))

    assert places(data, 's') == [('book', 1)]
    assert places(data, 'b') == [('book', 3), ('series', 'Dune')]


def test_absent_stored_items_are_skipped() -> None:
    library = FakeLibrary(types={'#date_read': 'datetime'})
    library.values['title'] = {1: 'Only'}
    library.values['#tier'] = {1: 's'}
    app = facade(library, {'s': [{'series': 'Gone'}, {'book': 1}, {'book': 99}]})

    data = app.compile(CompileRequest('library', (1,), 'Lib', '0.1.0'))

    assert places(data, 's') == [('book', 1)]


def test_a_narrower_compile_leaves_the_stored_order_alone() -> None:
    library = FakeLibrary(types={'#date_read': 'datetime'})
    library.values['title'] = {1: 'Only'}
    library.values['#tier'] = {1: 's'}
    order = {'s': [{'series': 'Dune'}, {'book': 1}]}
    prefs = FakePrefs({TIER_CONFIG_KEY: CONFIG.to_dict(), LANE_ORDER_KEY: order})
    app = TierList(library, prefs, lambda: TODAY, lambda: NOW, covers=FakeCovers())

    app.compile(CompileRequest('library', (1,), 'Lib', '0.1.0'))

    assert prefs.data[LANE_ORDER_KEY] == order


def test_an_empty_store_orders_cards_and_stacks_together_by_date_read() -> None:
    library = FakeLibrary(types={'#date_read': 'datetime'})
    library.values['title'] = {1: 'Early card', 3: 'Late card'}
    library.values['#tier'] = {1: 's', 2: 's', 3: 's'}
    library.values['#date_read'] = {1: date(2019, 1, 1), 2: date(2020, 1, 1), 3: date(2021, 1, 1)}
    library.values['series'] = {2: 'Dune'}
    library.values['series_index'] = {2: 1.0}
    app = facade(library)

    data = app.compile(CompileRequest('library', (1, 2, 3), 'Lib', '0.1.0'))

    assert places(data, 's') == [('book', 1), ('series', 'Dune'), ('book', 3)]

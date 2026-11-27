"""Arrange View staging: what each drop means, and what saving writes."""

from datetime import UTC, date, datetime

from fakes import FakeCovers, FakeLibrary, FakePrefs, FakeSavedSearches

from tierlist.app import TIER_CONFIG_KEY, TierList
from tierlist.arrange import Arrange, ArrangeItem
from tierlist.compile import CompileRequest
from tierlist.config_admin import ConfigAdmin
from tierlist.lane_order import LANE_ORDER_KEY
from tierlist.tiers import DEFAULT_TIER_CONFIG, Tier

NOW = datetime(2026, 11, 6, 12, 0, tzinfo=UTC)
TODAY = date(2026, 11, 6)
TIERS = (Tier('s', 'S', '#ff7f7f'), Tier('a', 'A', '#ffbf7f'), Tier('b', 'B', '#ffdf7f'))


def series(name: str) -> ArrangeItem:
    return ArrangeItem('series', name, name)


def card(book_id: int, title: str) -> ArrangeItem:
    return ArrangeItem('book', book_id, title)


def board(lanes: dict[str, list[ArrangeItem]]) -> Arrange:
    return Arrange(TIERS, lanes)


def keys(staged: Arrange, tier: str | None) -> list[str | int]:
    items = next(items for entry, items in staged.lanes() if (None if entry is None else entry.id) == tier)
    return [item.key for item in items]


def populated_library() -> FakeLibrary:
    """A two-book Dune series and two standalone books, all in Tier S; the last one is unread."""
    library = FakeLibrary(types={'#date_read': 'datetime'})
    library.values['title'] = {1: 'Dune', 2: 'Dune Messiah', 3: 'Read card', 4: 'Unread card'}
    library.values['series'] = {1: 'Dune', 2: 'Dune'}
    library.values['series_index'] = {1: 1.0, 2: 2.0}
    library.values['#tier'] = {1: 's', 2: 's', 3: 's', 4: 's'}
    library.values['#date_read'] = {1: date(2024, 1, 1), 2: date(2024, 1, 2), 3: date(2024, 1, 3)}
    return library


def admin_for(library: FakeLibrary) -> tuple[ConfigAdmin, FakePrefs]:
    prefs = FakePrefs({TIER_CONFIG_KEY: DEFAULT_TIER_CONFIG.to_dict()})
    return ConfigAdmin(library, prefs, FakeSavedSearches(), today=lambda: TODAY), prefs


def test_reorder_within_a_lane_moves_the_card() -> None:
    staged = board({'s': [card(1, 'One'), card(2, 'Two'), card(3, 'Three')]})
    assert staged.move('book', 3, 's', 0) is True
    assert keys(staged, 's') == [3, 1, 2]


def test_a_reorder_further_down_the_lane_lands_at_the_dropped_position() -> None:
    staged = board({'s': [card(1, 'One'), card(2, 'Two'), card(3, 'Three')]})
    staged.move('book', 1, 's', 2)
    assert keys(staged, 's') == [2, 1, 3]
    staged.move('book', 3, 's')
    assert keys(staged, 's') == [2, 1, 3]


def test_a_stack_dropped_on_another_lane_is_refused_and_changes_nothing() -> None:
    staged = board({'s': [series('Dune'), card(2, 'Two')], 'a': [card(3, 'Three')]})
    before = staged.order()
    assert staged.move('series', 'Dune', 'a', 0) is False
    assert staged.move('series', 'Dune', None, 0) is False
    assert staged.order() == before


def test_a_card_dropped_on_another_lane_is_refused_and_changes_nothing() -> None:
    staged = board({'s': [card(1, 'One'), card(2, 'Two')]})
    before = staged.order()
    assert staged.move('book', 1, 'a', 0) is False
    assert staged.move('book', 1, None, 0) is False
    assert staged.order() == before


def test_order_reports_each_non_empty_lane_in_staged_order() -> None:
    staged = board({'s': [series('Dune'), card(2, 'Two')]})
    assert staged.order() == {'s': [('series', 'Dune'), ('book', 2)]}


def test_the_arrange_board_holds_the_series_and_cards_with_their_cover_candidates() -> None:
    admin, _ = admin_for(populated_library())
    staged = admin.arrange()
    items = next(items for entry, items in staged.lanes() if entry is not None and entry.id == 's')
    assert [(item.kind, item.key) for item in items] == [('series', 'Dune'), ('book', 3), ('book', 4)]
    assert items[0].books == (1, 2)


def test_staging_a_drop_writes_nothing_until_it_is_saved() -> None:
    library = populated_library()
    admin, prefs = admin_for(library)
    values = {name: dict(column) for name, column in library.values.items()}
    stored = dict(prefs.data)
    staged = admin.arrange()
    staged.move('book', 4, 's', 0)
    assert prefs.data == stored and library.values == values


def test_saving_writes_only_lane_order_even_after_a_refused_cross_lane_drop() -> None:
    library = populated_library()
    admin, prefs = admin_for(library)
    staged = admin.arrange()
    staged.move('series', 'Dune', 'a', 0)
    staged.move('book', 4, 'b', 0)
    staged.move('book', 4, 's', 0)
    tiers = dict(library.values['#tier'])
    admin.save_arrange(staged)
    assert library.values['#tier'] == tiers and 4 not in library.values['#date_read']
    assert prefs.data[LANE_ORDER_KEY] == {'s': [{'book': 4}, {'series': 'Dune'}, {'book': 3}]}


def test_a_saved_arrangement_drives_the_next_compile() -> None:
    library = populated_library()
    admin, prefs = admin_for(library)
    staged = admin.arrange()
    staged.move('book', 4, 's', 0)
    admin.save_arrange(staged)
    data = TierList(library, prefs, lambda: TODAY, lambda: NOW, covers=FakeCovers()).compile(
        CompileRequest('library', (1, 2, 3, 4), 'Lib', '0.1.0')
    )
    lane_s = next(lane for lane in data.lanes if lane.tier == 's')
    items = [('series', item.stack) if item.stack else ('book', item.card) for item in lane_s.items]
    assert items == [('book', 4), ('series', 'Dune'), ('book', 3)]

"""Arrange View staging: what each drop means, and what saving writes."""

from datetime import UTC, date, datetime

from fakes import FakeCovers, FakeLibrary, FakePrefs, FakeSavedSearches

from tierlist.app import TIER_CONFIG_KEY, TierList
from tierlist.arrange import Arrange, ArrangeItem
from tierlist.compile import CompileRequest
from tierlist.config_admin import ConfigAdmin
from tierlist.lane_order import LANE_ORDER_KEY
from tierlist.series_tiers import SERIES_TIER_OVERRIDES_KEY
from tierlist.tiers import DEFAULT_TIER_CONFIG, Tier

NOW = datetime(2026, 11, 6, 12, 0, tzinfo=UTC)
TODAY = date(2026, 11, 6)
TIERS = (Tier('s', 'S', '#ff7f7f'), Tier('a', 'A', '#ffbf7f'), Tier('b', 'B', '#ffdf7f'))


def series(name: str) -> ArrangeItem:
    return ArrangeItem('series', name, name)


def card(book_id: int, title: str) -> ArrangeItem:
    return ArrangeItem('book', book_id, title)


def board(lanes: dict[str, list[ArrangeItem]], overrides: dict[str, str] | None = None) -> Arrange:
    return Arrange(TIERS, lanes, overrides or {})


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


def test_reorder_within_a_lane_moves_the_card_and_keeps_tiers_alone() -> None:
    staged = board({'s': [card(1, 'One'), card(2, 'Two'), card(3, 'Three')]})
    staged.move('book', 3, 's', 0)
    assert keys(staged, 's') == [3, 1, 2]
    assert staged.overrides() == {} and staged.book_tiers() == {}


def test_a_series_dropped_on_another_tier_lane_sets_its_override() -> None:
    staged = board({'s': [series('Dune')]})
    staged.move('series', 'Dune', 'a', 0)
    assert staged.overrides() == {'Dune': 'a'}
    assert keys(staged, 'a') == ['Dune'] and keys(staged, 's') == []


def test_a_series_dropped_on_the_lane_auto_would_pick_still_sets_an_override() -> None:
    staged = board({'b': [series('Dune')]})
    staged.move('series', 'Dune', 'a', 0)
    assert staged.overrides() == {'Dune': 'a'}


def test_a_series_dropped_on_unranked_clears_its_override_and_keeps_the_others() -> None:
    staged = board({'a': [series('Dune')]}, {'Dune': 'a', 'Other': 'b'})
    staged.move('series', 'Dune', None, 0)
    assert staged.overrides() == {'Other': 'b'}
    assert keys(staged, None) == ['Dune']


def test_a_book_dropped_on_a_tier_lane_sets_its_book_tier_and_on_unranked_clears_it() -> None:
    staged = board({'s': [card(1, 'One'), card(2, 'Two')]})
    staged.move('book', 1, 'a', 0)
    assert staged.book_tiers() == {1: 'a'}
    assert keys(staged, 'a') == [1]
    staged.move('book', 1, None, 0)
    assert staged.book_tiers() == {1: None}
    assert keys(staged, None) == [1]


def test_a_dropped_item_keeps_the_position_it_was_dropped_at() -> None:
    staged = board({'s': [card(1, 'One')], 'a': [card(2, 'Two'), card(3, 'Three')]})
    staged.move('book', 1, 'a', 1)
    assert keys(staged, 'a') == [2, 1, 3]


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
    staged.move('series', 'Dune', 'a', 0)
    staged.move('book', 4, 'b', 0)
    assert prefs.data == stored and library.values == values


def test_saving_writes_overrides_book_tiers_and_lane_order() -> None:
    library = populated_library()
    admin, prefs = admin_for(library)
    staged = admin.arrange()
    staged.move('series', 'Dune', 'a', 0)
    staged.move('book', 4, 'b', 0)
    admin.save_arrange(staged)
    assert prefs.data[SERIES_TIER_OVERRIDES_KEY] == {'Dune': 'a'}
    assert library.values['#tier'] == {1: 's', 2: 's', 3: 's', 4: 'b'}
    assert library.values['#date_read'][4] == TODAY
    assert prefs.data[LANE_ORDER_KEY] == {'s': [{'book': 3}], 'a': [{'series': 'Dune'}], 'b': [{'book': 4}]}


def test_a_saved_arrangement_drives_the_next_compile() -> None:
    library = populated_library()
    admin, prefs = admin_for(library)
    staged = admin.arrange()
    staged.move('series', 'Dune', 'a', 0)
    staged.move('book', 4, 'a', 1)
    admin.save_arrange(staged)
    data = TierList(library, prefs, lambda: TODAY, lambda: NOW, covers=FakeCovers()).compile(
        CompileRequest('library', (1, 2, 3, 4), 'Lib', '0.1.0')
    )
    lane_a = next(lane for lane in data.lanes if lane.tier == 'a')
    items = [('series', item.stack) if item.stack else ('book', item.card) for item in lane_a.items]
    assert items == [('series', 'Dune'), ('book', 4)]

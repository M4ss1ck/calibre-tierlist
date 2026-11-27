"""The Deciding Book: the highest-indexed book that is both read and tiered sets its series' Series Tier."""

from collections.abc import Mapping
from datetime import UTC, date, datetime

from fakes import FakeCovers, FakeLibrary, FakePrefs, lane_stacks

from tierlist.app import TIER_CONFIG_KEY, TierList
from tierlist.compile import CompileRequest, TierListData
from tierlist.tiers import Tier, TierConfig

NOW = datetime(2026, 11, 6, 12, 0, tzinfo=UTC)
TODAY = date(2026, 11, 6)
CONFIG = TierConfig(tiers=(Tier('s', 'S', '#ff7f7f'), Tier('a', 'A', '#ffbf7f'), Tier('b', 'B', '#ffdf7f')))
S, A, B, UNRANKED = 0, 1, 2, -1


def compile_dune(
    indexes: dict[int, float | None], tiers: dict[int, str], read: set[int], **extra: Mapping[int, object]
) -> TierListData:
    library = FakeLibrary(types={'#date_read': 'datetime'})
    app = TierList(
        library, FakePrefs({TIER_CONFIG_KEY: CONFIG.to_dict()}), lambda: TODAY, lambda: NOW, covers=FakeCovers()
    )
    library.values['series'] = {book_id: 'Dune' for book_id in indexes}
    library.values['series_index'] = dict(indexes)
    library.values['#tier'] = dict(tiers)
    library.values['#date_read'] = {book_id: TODAY for book_id in read}
    library.values.update({name: dict(column) for name, column in extra.items()})
    return app.compile(CompileRequest('library', tuple(indexes), 'Lib', '0.1.0'))


def lane_of(data: TierListData, name: str = 'Dune') -> int:
    for number, lane in enumerate(data.lanes):
        if name in lane_stacks(lane):
            return number - len(data.lanes) if lane.tier is None else number
    raise AssertionError(f'{name} is on no Lane')


def deciding(data: TierListData, name: str = 'Dune') -> object:
    return data.to_dict()['series'][name]['decidingBook']


def test_the_highest_index_wins_over_a_lower_index_with_a_better_tier() -> None:
    data = compile_dune({1: 1.0, 2: 2.0}, {1: 's', 2: 'b'}, {1, 2})

    assert lane_of(data) == B
    assert deciding(data) == '2'


def test_a_tiered_but_unread_book_is_skipped() -> None:
    data = compile_dune({1: 1.0, 2: 2.0}, {1: 'a', 2: 's'}, {1})

    assert lane_of(data) == A
    assert deciding(data) == '1'


def test_a_read_but_untiered_book_is_skipped() -> None:
    data = compile_dune({1: 1.0, 2: 2.0}, {1: 'a'}, {1, 2})

    assert lane_of(data) == A


def test_a_tie_on_index_goes_to_the_most_recently_modified_book() -> None:
    modified = {1: datetime(2026, 5, 1, tzinfo=UTC), 2: datetime(2026, 1, 1, tzinfo=UTC)}

    data = compile_dune({1: 2.0, 2: 2.0}, {1: 's', 2: 'b'}, {1, 2}, last_modified=modified)

    assert lane_of(data) == S
    assert deciding(data) == '1'


def test_a_tie_on_index_and_modified_goes_to_the_higher_id() -> None:
    same = datetime(2026, 5, 1, tzinfo=UTC)

    data = compile_dune({1: 2.0, 2: 2.0}, {1: 's', 2: 'b'}, {1, 2}, last_modified={1: same, 2: same})

    assert deciding(data) == '2'


def test_a_book_tier_naming_a_deleted_tier_is_skipped() -> None:
    data = compile_dune({1: 1.0, 2: 2.0}, {1: 'a', 2: 'gone'}, {1, 2})

    assert lane_of(data) == A
    assert deciding(data) == '1'


def test_no_candidate_puts_the_series_in_the_unranked_lane() -> None:
    data = compile_dune({1: 1.0, 2: 2.0}, {2: 's'}, {1})

    assert lane_of(data) == UNRANKED
    assert deciding(data) is None


def test_a_fractional_index_beats_the_whole_number_below_it() -> None:
    data = compile_dune({1: 2.0, 2: 2.5}, {1: 's', 2: 'b'}, {1, 2})

    assert deciding(data) == '2'


def test_a_book_with_no_index_reads_as_one() -> None:
    data = compile_dune({1: None, 2: 1.5}, {1: 's', 2: 'b'}, {1, 2})

    assert deciding(data) == '2'
    assert lane_of(data) == B


def test_stored_overrides_from_an_older_version_are_ignored() -> None:
    library = FakeLibrary(types={'#date_read': 'datetime'})
    prefs = FakePrefs({TIER_CONFIG_KEY: CONFIG.to_dict(), 'series_tier_overrides': {'Dune': 's'}})
    app = TierList(library, prefs, lambda: TODAY, lambda: NOW, covers=FakeCovers())
    library.values.update(
        {'series': {1: 'Dune'}, 'series_index': {1: 1.0}, '#tier': {1: 'b'}, '#date_read': {1: TODAY}}
    )

    data = app.compile(CompileRequest('library', (1,), 'Lib', '0.1.0'))

    assert lane_of(data) == B

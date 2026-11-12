"""Compile Series Tiers through the facade: majorities, ties, and which books join a Stack."""

from datetime import UTC, date, datetime

from fakes import FakeCovers, FakeLibrary, FakePrefs, lane_cards, lane_stacks

from tierlist.app import TIER_CONFIG_KEY, TierList
from tierlist.compile import CompileRequest
from tierlist.tiers import Tier, TierConfig

NOW = datetime(2026, 11, 6, 12, 0, tzinfo=UTC)
TODAY = date(2026, 11, 6)
CONFIG = TierConfig(tiers=(Tier('s', 'S', '#ff7f7f'), Tier('a', 'A', '#ffbf7f'), Tier('b', 'B', '#ffdf7f')))


def request(*book_ids: int) -> CompileRequest:
    return CompileRequest('library', book_ids, 'Lib', '0.1.0')


def facade() -> tuple[TierList, FakeLibrary]:
    library = FakeLibrary(types={'#date_read': 'datetime'})
    prefs = FakePrefs({TIER_CONFIG_KEY: CONFIG.to_dict()})
    return TierList(library, prefs, lambda: TODAY, lambda: NOW, covers=FakeCovers()), library


def dune(library: FakeLibrary, *book_ids: int) -> None:
    library.values['series'] = {book_id: 'Dune' for book_id in book_ids}
    library.values['series_index'] = {book_id: float(index) for index, book_id in enumerate(book_ids, 1)}


def test_a_clear_majority_tier_wins() -> None:
    app, library = facade()
    dune(library, 1, 2, 3)
    library.values['#tier'] = {1: 's', 2: 's', 3: 'a'}

    data = app.compile(request(1, 2, 3))

    assert lane_stacks(data.lanes[0]) == ('Dune',)
    assert lane_stacks(data.lanes[1]) == ()


def test_a_tie_goes_to_the_lower_tier() -> None:
    app, library = facade()
    dune(library, 1, 2)
    library.values['#tier'] = {1: 's', 2: 'a'}

    data = app.compile(request(1, 2))

    assert lane_stacks(data.lanes[0]) == ()
    assert lane_stacks(data.lanes[1]) == ('Dune',)


def test_a_single_tiered_book_places_the_series() -> None:
    app, library = facade()
    dune(library, 1)
    library.values['#tier'] = {1: 'b'}

    data = app.compile(request(1))

    assert lane_stacks(data.lanes[2]) == ('Dune',)


def test_only_unranked_read_books_put_the_series_in_the_unranked_lane() -> None:
    app, library = facade()
    dune(library, 1, 2)
    library.values['#date_read'] = {1: TODAY, 2: TODAY}

    data = app.compile(request(1, 2))

    assert lane_stacks(data.lanes[-1]) == ('Dune',)


def test_an_owned_unread_member_is_in_books_and_not_read() -> None:
    app, library = facade()
    dune(library, 1, 2)
    library.values['#tier'] = {1: 's'}

    data = app.compile(request(1, 2))

    unread = next(book for book in data.books if book.id == 2)
    assert unread.read is False
    assert data.to_dict()['books']['2']['read'] is False


def test_a_standalone_book_stays_a_card_and_never_a_stack() -> None:
    app, library = facade()
    dune(library, 2)
    library.values['#tier'] = {1: 's', 2: 's'}

    data = app.compile(request(1, 2))

    assert lane_cards(data.lanes[0]) == (1,)
    assert lane_stacks(data.lanes[0]) == ('Dune',)
    assert 'Dune' in data.series

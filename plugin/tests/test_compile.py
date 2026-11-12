"""Compile through the facade: Lanes, Book Tiers, Read State, order, and output paths."""

from collections.abc import Mapping
from datetime import UTC, date, datetime
from pathlib import Path

from fakes import FakeLibrary, FakePrefs, lane_cards

from tierlist.app import TIER_CONFIG_KEY, TierList
from tierlist.compile import CompileRequest
from tierlist.compile.build import count_series
from tierlist.tiers import TierConfig

NOW = datetime(2026, 11, 6, 12, 0, tzinfo=UTC)
TODAY = date(2026, 11, 6)


def request(*book_ids: int) -> CompileRequest:
    return CompileRequest('library', book_ids, 'Lib', '0.1.0')


def facade(
    types: Mapping[str, str] | None = None, config: TierConfig | None = None
) -> tuple[TierList, FakeLibrary, FakePrefs]:
    library = FakeLibrary(types=types)
    prefs = FakePrefs({} if config is None else {TIER_CONFIG_KEY: config.to_dict()})
    return TierList(library, prefs, lambda: TODAY, lambda: NOW), library, prefs


def test_lanes_follow_tier_config_order_then_unranked() -> None:
    app, library, _ = facade({'#date_read': 'datetime'})
    library.values['title'] = {1: 'One'}
    library.values['#date_read'] = {1: TODAY}

    data = app.compile(request(1))

    assert [lane.tier for lane in data.lanes] == ['s', 'a', 'b', 'c', 'd', 'f', None]
    assert lane_cards(data.lanes[-1]) == (1,)
    assert data.books[0].tier is None


def test_read_untiered_books_go_to_the_unranked_lane() -> None:
    app, library, _ = facade({'#date_read': 'datetime'})
    library.values['title'] = {1: 'Read'}
    library.values['#date_read'] = {1: TODAY}
    library.values['#tier'] = {}

    data = app.compile(request(1))

    assert lane_cards(data.lanes[-1]) == (1,)
    assert all(lane_cards(lane) == () for lane in data.lanes[:-1])


def test_unread_books_are_excluded() -> None:
    app, library, _ = facade({'#date_read': 'datetime'})
    library.values['title'] = {1: 'Read', 2: 'Unread'}
    library.values['#date_read'] = {1: TODAY}

    data = app.compile(request(1, 2))

    assert [book.id for book in data.books] == [1]
    assert all(2 not in lane_cards(lane) for lane in data.lanes)


def test_a_tiered_book_without_a_read_date_is_included() -> None:
    app, library, _ = facade({'#date_read': 'datetime'})
    library.values['title'] = {1: 'Tiered'}
    library.values['#tier'] = {1: 'a'}

    data = app.compile(request(1))

    assert lane_cards(data.lanes[1]) == (1,)
    assert data.books[0].date_read is None


def test_an_unknown_tier_id_goes_to_the_unranked_lane() -> None:
    app, library, _ = facade({'#date_read': 'datetime'})
    library.values['title'] = {1: 'Odd'}
    library.values['#tier'] = {1: 'z'}

    data = app.compile(request(1))

    assert data.books[0].tier is None
    assert lane_cards(data.lanes[-1]) == (1,)


def test_cards_order_by_date_read_then_undated_then_title_then_id() -> None:
    app, library, _ = facade({'#date_read': 'datetime'})
    library.values['title'] = {1: 'Alpha', 2: 'zeta', 3: 'beta', 4: 'Undated'}
    library.values['#tier'] = {1: 's', 2: 's', 3: 's', 4: 's'}
    library.values['#date_read'] = {1: date(2021, 1, 1), 2: date(2020, 1, 1), 3: date(2021, 1, 1)}

    data = app.compile(request(1, 2, 3, 4))

    assert lane_cards(data.lanes[0]) == (2, 1, 3, 4)


def test_bool_read_column_yields_no_date_and_honours_false() -> None:
    app, library, _ = facade({'#date_read': 'bool'})
    library.values['title'] = {1: 'Yes', 2: 'No'}
    library.values['#date_read'] = {1: True, 2: False}

    data = app.compile(request(1, 2))

    assert [book.id for book in data.books] == [1]
    assert data.books[0].date_read is None
    assert data.to_dict()['books']['1']['dateRead'] is None


def test_tz_aware_read_state_uses_its_local_date() -> None:
    app, library, _ = facade({'#date_read': 'datetime'})
    moment = datetime(2024, 1, 10, 20, 0, tzinfo=UTC)
    library.values['title'] = {1: 'One'}
    library.values['#date_read'] = {1: moment}

    data = app.compile(request(1))

    assert data.books[0].date_read == moment.astimezone().date()


def test_output_path_defaults_under_the_home_directory() -> None:
    app, _, _ = facade()

    expected = Path.home() / 'Tierlists' / f'tierlist-{TODAY.isoformat()}.html'

    assert app.output_path() == str(expected)


def test_remember_output_path_round_trips() -> None:
    app, _, _ = facade()
    app.remember_output_path('/tmp/tierlist.html')

    assert app.output_path() == '/tmp/tierlist.html'


def test_series_count_counts_distinct_non_empty_values() -> None:
    library = FakeLibrary()
    library.values['series'] = {1: 'Dune', 2: 'Dune', 3: '', 4: None}

    assert count_series(library, [1, 2, 3, 4]) == 1

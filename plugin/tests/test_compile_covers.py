"""Compile covers through the facade: on-board books only, the chosen format, and the data URI."""

from datetime import UTC, date, datetime
from pathlib import Path

from fakes import FakeCovers, FakeLibrary, FakePrefs

from tierlist.app import TierList
from tierlist.compile import COVER_WIDTH, CompileRequest
from tierlist.publish import MARKER

NOW = datetime(2026, 11, 6, 12, 0, tzinfo=UTC)
TODAY = date(2026, 11, 6)
PREFIX = '<script>const DATA = '
SUFFIX = ';</script>'


def request(*book_ids: int) -> CompileRequest:
    return CompileRequest('library', book_ids, 'Lib', '0.1.0')


def facade(covers: FakeCovers) -> tuple[TierList, FakeLibrary]:
    library = FakeLibrary(types={'#date_read': 'datetime'})
    prefs = FakePrefs()
    app = TierList(library, prefs, lambda: TODAY, lambda: NOW, covers=covers)
    return app, library


def test_covers_hold_one_entry_per_on_board_book_that_has_one() -> None:
    app, library = facade(FakeCovers(with_cover={1}))
    library.values['title'] = {1: 'Has Cover', 2: 'No Cover'}
    library.values['#tier'] = {1: 's', 2: 's'}

    data = app.compile(request(1, 2))

    assert set(data.covers) == {1}
    assert data.covers[1].colour == '#336699'


def test_unread_books_are_never_asked_for_a_cover() -> None:
    covers = FakeCovers(with_cover={1, 2})
    app, library = facade(covers)
    library.values['title'] = {1: 'Read', 2: 'Unread'}
    library.values['#date_read'] = {1: TODAY}

    app.compile(request(1, 2))

    assert covers.calls == [(1, 'webp', COVER_WIDTH)]


def test_each_cover_is_asked_for_the_chosen_format_and_thumbnail_width() -> None:
    covers = FakeCovers(formats=frozenset({'avif', 'jpeg'}), with_cover={1})
    app, library = facade(covers)
    library.values['title'] = {1: 'One'}
    library.values['#tier'] = {1: 's'}

    app.compile(request(1))

    assert covers.calls == [(1, 'avif', COVER_WIDTH)]


def test_to_dict_embeds_each_cover_as_a_webp_data_uri() -> None:
    app, library = facade(FakeCovers(with_cover={1}))
    library.values['title'] = {1: 'One'}
    library.values['#tier'] = {1: 's'}

    payload = app.compile(request(1)).to_dict()

    assert payload['covers']['1']['src'].startswith('data:image/webp;base64,')


def test_compile_to_file_logs_the_cover_count_and_format(tmp_path: Path) -> None:
    app, library = facade(FakeCovers(with_cover={1}))
    library.values['title'] = {1: 'One'}
    library.values['#tier'] = {1: 's'}
    logs: list[str] = []

    app.compile_to_file(request(1), f'{PREFIX}{MARKER}{SUFFIX}', tmp_path / 'tierlist.html', logs.append)

    assert '1 covers as webp' in logs[0]

"""Integration test for Series Tier Overrides through the real menu and prefs.

Run with ``calibre-debug -e plugin/itest/series_override.py`` after installing
``dist/tierlist.zip`` with ``calibre-customize -a`` into a throwaway
``CALIBRE_CONFIG_DIRECTORY``. Prints ``SERIES OVERRIDE OK`` and exits 0 on success.

calibre runs Python with -OO, which strips ``assert``; use ``expect``.
"""

import sys
import tempfile
from typing import Any

from calibre.ebooks.metadata.book.base import Metadata
from calibre.gui2 import Application
from calibre.library import db as open_db
from calibre_plugins.tierlist.app import TierList
from calibre_plugins.tierlist.calibre_ui.adapters import tier_list
from calibre_plugins.tierlist.compile import CompileRequest, TierListData
from fake_gui import FakeGui, load_action, menu_shortcuts

SERIES_NAMES = (*(f'Set series tier: {label}' for label in 'SABCDF'), 'Set series tier: Auto')
DUNE = 'Dune'
EARTHSEA = 'Earthsea'
RENAMED = 'Dune Messiah'


def expect(ok: bool, message: object) -> None:
    if not ok:
        raise SystemExit(f'SERIES OVERRIDE FAIL: {message}')


def book(db: Any, title: str, series: str | None = None, index: float = 1.0) -> int:
    book_id = db.new_api.create_book_entry(Metadata(title, ['Author']))
    if series is not None:
        db.new_api.set_field('series', {book_id: series})
        db.new_api.set_field('series_index', {book_id: index})
    return book_id


def library(path: str) -> tuple[Any, list[int], list[int]]:
    """A library with two series and one standalone book, both series ranked S."""
    db = open_db(path)
    db.create_custom_column('tier', 'Tier', 'text', False)
    db.close()
    db = open_db(path)
    dune = [book(db, f'Dune {n}', DUNE, float(n)) for n in (1, 2)]
    earthsea = book(db, 'A Wizard of Earthsea', EARTHSEA)
    standalone = book(db, 'Standalone')
    app = tier_list(db)
    app.set_book_tier([*dune, earthsea], 's')
    app.mark_tier_column_offered()  # skip the first-run question dialogs
    app.mark_read_column_offered()
    return db, dune, [earthsea, standalone]


def shortcut(gui: Any, action: Any, name: str) -> Any:
    return next(item['action'] for item in menu_shortcuts(gui, action).values() if item['name'] == name)


def compiled(app: TierList, ids: list[int]) -> TierListData:
    return app.compile(CompileRequest('library', tuple(sorted(ids)), 'Lib', '0.1.0'))


def stacks(data: TierListData, tier: str) -> tuple[str, ...]:
    return next(lane.stacks for lane in data.lanes if lane.tier == tier)


def check_menu(db: Any, dune: list[int], others: list[int]) -> None:
    """An Override set through the menu survives into a new facade and a Compile."""
    selected = dune[0]
    gui = FakeGui(db, [selected])
    action = load_action(gui)
    names = {item['name'] for item in menu_shortcuts(gui, action).values()}
    expect(set(SERIES_NAMES) <= names, f'missing series shortcuts: {sorted(names)}')
    titles = [item.text() for item in action.qaction.menu().actions()]
    expect('Set series tier' in titles, titles)

    shortcut(gui, action, 'Set series tier: A').trigger()
    expect(gui.library_view.model().refreshed == [[selected]], 'refresh_ids was not called for the selection')
    reopened = tier_list(db)
    expect(reopened.series_tier_overrides() == {DUNE: 'a'}, reopened.series_tier_overrides())

    dune.append(book(db, 'Dune 3', DUNE, 3.0))
    data = compiled(tier_list(db), [*dune, *others])
    expect(stacks(data, 'a') == (DUNE,), stacks(data, 'a'))
    expect(DUNE not in stacks(data, 's'), stacks(data, 's'))
    expect(data.series[DUNE].override is True, data.series[DUNE])
    expect([position.book for position in data.series[DUNE].positions] == dune, data.series[DUNE].positions)

    shortcut(gui, action, 'Set series tier: Auto').trigger()
    expect(tier_list(db).series_tier_overrides() == {}, tier_list(db).series_tier_overrides())
    data = compiled(tier_list(db), [*dune, *others])
    expect(stacks(data, 'a') == (), stacks(data, 'a'))
    expect(DUNE in stacks(data, 's'), stacks(data, 's'))
    expect(data.series[DUNE].override is False, data.series[DUNE].override)

    shortcut(gui, action, 'Set series tier: A').trigger()
    expect(tier_list(db).series_tier_overrides() == {DUNE: 'a'}, tier_list(db).series_tier_overrides())
    db.new_api.set_field('series', {book_id: RENAMED for book_id in dune})
    expect(tier_list(db).series_tier_orphans() == [DUNE], tier_list(db).series_tier_orphans())


def main() -> int:
    Application([])
    with tempfile.TemporaryDirectory() as tmp:
        db, dune, others = library(tmp + '/series')
        try:
            check_menu(db, dune, others)
        finally:
            db.close()
    print('SERIES OVERRIDE OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())

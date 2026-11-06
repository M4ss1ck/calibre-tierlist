"""Integration test for Read State: Mark read, Mark unread, and the read column offers.

Run with ``calibre-debug -e plugin/itest/read_state.py`` after installing
``dist/tierlist.zip`` with ``calibre-customize -a`` into a throwaway
``CALIBRE_CONFIG_DIRECTORY``. Prints ``READ STATE OK`` and exits 0 on success.

calibre runs Python with -OO, which strips ``assert``; use ``expect``.
"""

import sys
import tempfile
from datetime import date, datetime
from typing import Any

from calibre.ebooks.metadata.book.base import Metadata
from calibre.gui2 import Application
from calibre.library import db as open_db
from calibre.utils.date import local_tz
from calibre_plugins.tierlist.app import TierList
from calibre_plugins.tierlist.calibre_ui.adapters import tier_list
from fake_gui import FakeGui, load_action, menu_shortcuts

READ_NAMES = ('Mark read', 'Mark unread')


def expect(ok: bool, message: object) -> None:
    if not ok:
        raise SystemExit(f'READ STATE FAIL: {message}')


def new_books(db: Any) -> list[int]:
    return [db.new_api.create_book_entry(Metadata(f'Book {n}', ['Author'])) for n in (1, 2, 3)]


def open_library(path: str, *columns: tuple[str, str, str]) -> Any:
    db = open_db(path)
    for lookup, heading, datatype in columns:
        db.create_custom_column(lookup, heading, datatype, False)
    db.close()
    return open_db(path)


def check_date_column(path: str) -> tuple[Any, list[int]]:
    """A date column is marked read once, preserving an existing date."""
    db = open_library(path, ('date_read', 'Date read', 'datetime'), ('tier', 'Tier', 'text'))
    ids = new_books(db)
    app: TierList = tier_list(db)
    expect(app.read_column_ready(), 'date read column not ready after reopening')
    old = datetime(2000, 1, 1, 12, tzinfo=local_tz)
    db.new_api.set_field('#date_read', {ids[0]: old})
    app.set_book_tier(ids, 'a')
    expect(db.new_api.field_for('#tier', ids[0]) == 'a', 'first book not tiered')
    expect(db.new_api.field_for('#tier', ids[2]) == 'a', 'third book not tiered')
    kept = db.new_api.field_for('#date_read', ids[0])
    expect(kept is not None and kept.year == 2000, f'pre-seeded read date changed: {kept}')
    first = db.new_api.field_for('#date_read', ids[1])
    expect(first is not None and first.astimezone(local_tz).date() == date.today(), f'read date not today: {first}')
    app.set_book_tier(ids, 'a')
    expect(db.new_api.field_for('#date_read', ids[1]) == first, 'mark read overwrote an existing date')
    app.clear_book_tier(ids)
    expect(db.new_api.field_for('#tier', ids[1]) is None, 'clear_book_tier kept the tier')
    expect(db.new_api.field_for('#date_read', ids[1]) == first, 'clear_book_tier cleared the read date')
    app.set_book_tier([ids[1]], 'a')
    app.mark_unread(ids)
    expect(db.new_api.field_for('#tier', ids[1]) is None, 'mark_unread kept the tier')
    expect(db.new_api.field_for('#date_read', ids[1]) is None, 'mark_unread kept the read date')
    return db, ids


def check_bool_column(path: str) -> None:
    """A bool column can be mapped as the Read State column."""
    db = open_library(path, ('read', 'Read', 'bool'), ('tier', 'Tier', 'text'))
    ids = new_books(db)
    app: TierList = tier_list(db)
    expect(not app.read_column_ready(), 'read column ready before it was mapped')
    expect(app.read_column_candidates() == ['#read'], app.read_column_candidates())
    app.map_read_column('#read')
    db.close()
    db = open_db(path)
    try:
        app = tier_list(db)
        expect(app.read_column_ready(), 'mapped bool column not ready after reopening')
        app.set_book_tier(ids[:1], 'a')
        expect(db.new_api.field_for('#read', ids[0]) is True, 'set_book_tier did not mark the book read')
        app.mark_unread(ids)
        expect(db.new_api.field_for('#read', ids[0]) is None, 'mark_unread kept the bool')
    finally:
        db.close()


def check_menu(db: Any, book_id: int) -> None:
    """Mark read and Mark unread appear beside Send to tier and survive rebuilds."""
    app: TierList = tier_list(db)
    app.mark_tier_column_offered()  # skip the first-run question dialog
    app.mark_read_column_offered()
    gui = FakeGui(db, [book_id])
    action = load_action(gui)
    shortcuts = menu_shortcuts(gui, action)
    expect(len(shortcuts) == 9, f'expected 9 menu shortcuts, got {len(shortcuts)}')
    names = {item['name'] for item in shortcuts.values()}
    expect(set(READ_NAMES) <= names, f'missing read shortcuts: {sorted(names)}')
    live_actions = len(gui.actions())
    menu = action.qaction.menu()
    expect(menu is not None, 'the action has no menu')
    for _ in range(2):
        menu.aboutToShow.emit()
        expect(len(menu_shortcuts(gui, action)) == 9, 'rebuild left the wrong number of shortcuts')
        expect(len(gui.actions()) == live_actions, 'rebuild left stale actions holding shortcuts on the gui')
    mark_read = next(item for item in menu_shortcuts(gui, action).values() if item['name'] == 'Mark read')
    mark_read['action'].trigger()
    stored = db.new_api.field_for('#date_read', book_id)
    expect(
        stored is not None and stored.astimezone(local_tz).date() == date.today(),
        f'Mark read did not write today: {stored}',
    )
    expect(gui.library_view.model().refreshed == [[book_id]], 'refresh_ids was not called for the selection')


def main() -> int:
    Application([])
    with tempfile.TemporaryDirectory() as tmp:
        db, ids = check_date_column(tmp + '/date-read')
        try:
            check_menu(db, ids[0])
        finally:
            db.close()
        check_bool_column(tmp + '/bool-read')
    print('READ STATE OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())

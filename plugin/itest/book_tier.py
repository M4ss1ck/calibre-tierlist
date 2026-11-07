"""Integration test for Send to tier and Clear tier.

Run with ``calibre-debug -e plugin/itest/book_tier.py`` after installing
``dist/tierlist.zip`` with ``calibre-customize -a`` into a throwaway
``CALIBRE_CONFIG_DIRECTORY``. Prints ``BOOK TIER OK`` and exits 0 on success.

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
from fake_gui import FakeGui, load_action, menu_shortcuts

TIER_NAMES = (*(f'Send to tier: {label}' for label in 'SABCDF'), 'Clear tier')
SERIES_NAMES = (*(f'Set series tier: {label}' for label in 'SABCDF'), 'Set series tier: Auto')


def expect(ok: bool, message: object) -> None:
    if not ok:
        raise SystemExit(f'BOOK TIER FAIL: {message}')


def check_adapters(path: str) -> tuple[Any, int]:
    db = open_db(path)
    expect(not tier_list(db).tier_column_ready(), 'tier column present before it was created')
    db.create_custom_column('tier', 'Tier', 'text', False)
    db.close()
    db = open_db(path)
    ids = [db.new_api.create_book_entry(Metadata(f'Book {n}', ['Author'])) for n in (1, 2, 3)]
    app: TierList = tier_list(db)
    expect(app.tier_column_ready(), 'tier column missing after reopening')
    expect('#tier' in db.field_metadata, '#tier not in field_metadata')
    app.set_book_tier(ids[:2], 'a')
    expect(db.new_api.field_for('#tier', ids[0]) == 'a', 'first book not written')
    expect(db.new_api.field_for('#tier', ids[1]) == 'a', 'second book not written')
    expect(db.new_api.field_for('#tier', ids[2]) is None, 'unselected book was written')
    app.clear_book_tier([ids[0]])
    expect(db.new_api.field_for('#tier', ids[0]) is None, 'clear did not remove the value')
    app.mark_tier_column_offered()
    app.mark_read_column_offered()
    db.close()
    db = open_db(path)
    expect(tier_list(db).tier_column_offered(), 'the offer flag did not persist')
    return db, ids[2]


def check_missing_column(path: str) -> None:
    """Without a tier column the submenu only explains why and offers creation."""
    db = open_db(path)
    tier_list(db).mark_tier_column_offered()  # skip the first-run question dialogs
    tier_list(db).mark_read_column_offered()
    gui = FakeGui(db, [])
    action = load_action(gui)
    names = {item['name'] for item in menu_shortcuts(gui, action).values()}
    expect(names == set(SERIES_NAMES), f'shortcuts without a tier column were {sorted(names)}')
    items = action.tier_menu._submenu.actions()
    expect([a.isEnabled() for a in items] == [False, True], [a.text() for a in items])
    db.close()


def check_menu(db: Any, book_id: int) -> None:
    gui = FakeGui(db, [book_id])
    action = load_action(gui)
    shortcuts = menu_shortcuts(gui, action)
    expect(len(shortcuts) == 14, f'expected 14 menu shortcuts, got {len(shortcuts)}')
    expect(
        sorted(item['name'] for item in shortcuts.values()) == sorted((*TIER_NAMES, *SERIES_NAMES)),
        'wrong shortcut names',
    )
    expect(all(item['default_keys'] == () for item in shortcuts.values()), 'a menu shortcut has a default key')
    live_actions = len(gui.actions())
    menu = action.qaction.menu()
    expect(menu is not None, 'the action has no menu')
    for _ in range(2):
        menu.aboutToShow.emit()
        expect(len(menu_shortcuts(gui, action)) == 14, 'rebuild left the wrong number of shortcuts')
        expect(len(gui.actions()) == live_actions, 'rebuild left stale actions holding shortcuts on the gui')
    shortcuts = menu_shortcuts(gui, action)
    tier_s = next(item for item in shortcuts.values() if item['name'] == 'Send to tier: S')
    tier_s['action'].trigger()
    expect(db.new_api.field_for('#tier', book_id) == 's', 'Send to tier: S did not write the tier')
    expect(gui.library_view.model().refreshed == [[book_id]], 'refresh_ids was not called for the selection')


def main() -> int:
    Application([])
    with tempfile.TemporaryDirectory() as tmp:
        db, book_id = check_adapters(tmp + '/tiered')
        try:
            check_menu(db, book_id)
        finally:
            db.close()
        check_missing_column(tmp + '/no-column')
    print('BOOK TIER OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())

"""Integration test for Send to tier and Clear tier.

Run with ``calibre-debug -e plugin/itest/book_tier.py`` after installing
``dist/tierlist.zip`` with ``calibre-customize -a`` into a throwaway
``CALIBRE_CONFIG_DIRECTORY``. Prints ``BOOK TIER OK`` and exits 0 on success.

calibre runs Python with -OO, which strips ``assert``; use ``expect``.
"""

import importlib
import sys
import tempfile
from typing import Any

from calibre.customize.ui import find_plugin
from calibre.ebooks.metadata.book.base import Metadata
from calibre.gui2 import Application
from calibre.gui2.keyboard import Manager
from calibre.library import db as open_db
from calibre_plugins.tierlist.app import TierList
from calibre_plugins.tierlist.calibre_ui.adapters import tier_list
from qt.core import QMainWindow

NAME = 'Tier List'
TIER_NAMES = (*(f'Send to tier: {label}' for label in 'SABCDF'), 'Clear tier')


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
    db.close()
    db = open_db(path)
    expect(tier_list(db).tier_column_offered(), 'the offer flag did not persist')
    return db, ids[2]


class FakeModel:
    def __init__(self, db: Any) -> None:
        self.db = db
        self.refreshed: list[list[int]] = []

    def refresh_ids(self, ids: list[int]) -> None:
        self.refreshed.append(list(ids))


class FakeLibraryView:
    def __init__(self, db: Any, ids: list[int]) -> None:
        self._ids = ids
        self._model = FakeModel(db)

    def get_selected_ids(self) -> list[int]:
        return list(self._ids)

    def model(self) -> FakeModel:
        return self._model


class FakeGui(QMainWindow):
    def __init__(self, db: Any, ids: list[int]) -> None:
        super().__init__()
        self.keyboard = Manager(self)
        self.current_db = db
        self.library_view = FakeLibraryView(db, ids)
        self.must_restart_before_config = False


def menu_shortcuts(gui: Any, action: Any) -> dict[str, dict[str, Any]]:
    prefix = f'{action.unique_name} : menu action : '
    return {name: shortcut for name, shortcut in gui.keyboard.shortcuts.items() if name.startswith(prefix)}


def load_action(gui: Any) -> Any:
    plugin = find_plugin(NAME)
    if plugin is None or plugin.actual_plugin is None:
        raise SystemExit('BOOK TIER FAIL: the Tier List plugin is not registered')
    # load_actual_plugin caches one action per plugin; each check needs its own gui.
    module_name, class_name = plugin.actual_plugin.split(':')
    action = getattr(importlib.import_module(module_name), class_name)(gui, plugin.site_customization)
    action.interface_action_base_plugin = plugin
    action.do_genesis()
    action.initialization_complete()
    return action


def check_missing_column(path: str) -> None:
    """Without a tier column the submenu only explains why and offers creation."""
    db = open_db(path)
    tier_list(db).mark_tier_column_offered()  # skip the first-run question dialog
    gui = FakeGui(db, [])
    action = load_action(gui)
    expect(not menu_shortcuts(gui, action), 'tier shortcuts registered without a tier column')
    items = action.tier_menu._submenu.actions()
    expect([a.isEnabled() for a in items] == [False, True], [a.text() for a in items])
    db.close()


def check_menu(db: Any, book_id: int) -> None:
    gui = FakeGui(db, [book_id])
    action = load_action(gui)
    shortcuts = menu_shortcuts(gui, action)
    expect(len(shortcuts) == 7, f'expected 7 menu shortcuts, got {len(shortcuts)}')
    expect(sorted(item['name'] for item in shortcuts.values()) == sorted(TIER_NAMES), 'wrong shortcut names')
    expect(all(item['default_keys'] == () for item in shortcuts.values()), 'a menu shortcut has a default key')
    menu = action.qaction.menu()
    expect(menu is not None, 'the action has no menu')
    for _ in range(2):
        menu.aboutToShow.emit()
        expect(len(menu_shortcuts(gui, action)) == 7, 'rebuild left the wrong number of shortcuts')
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

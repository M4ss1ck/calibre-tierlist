"""Integration test for Settings: the menu item, the tabbed widget, OK and Cancel.

Run with ``calibre-debug -e plugin/itest/settings.py`` after installing
``dist/tierlist.zip`` with ``calibre-customize -a`` into a throwaway
``CALIBRE_CONFIG_DIRECTORY``. Prints ``SETTINGS OK`` and exits 0 on success.
The file and message box dialogs are stubbed: offscreen Qt cannot click a
modal dialog; the widget itself is driven through its public methods and slots.

calibre runs Python with -OO, which strips ``assert``; use ``expect``.
"""

import sys
import tempfile
from typing import Any

from calibre.gui2 import Application
from calibre.library import db as open_db
from calibre_plugins.tierlist.calibre_ui import action as action_module
from calibre_plugins.tierlist.calibre_ui.adapters import config_admin, tier_list
from calibre_plugins.tierlist.calibre_ui.settings_dialog import SettingsDialog
from fake_gui import FakeGui, load_action
from qt.core import QPushButton

ID, LABEL = 0, 1
ITEM = 'Settings…'
OPENED: list[Any] = []


def expect(ok: bool, message: object) -> None:
    if not ok:
        raise SystemExit(f'SETTINGS FAIL: {message}')


class FakeDialog:
    """Stands in for SettingsDialog, recording that the menu item opened it."""

    def __init__(self, gui: Any) -> None:
        self.gui = gui
        OPENED.append(self)

    def exec(self) -> int:
        return 0


def cell(table: Any, row: int, column: int) -> Any:
    item = table.item(row, column)
    expect(item is not None, f'no cell at ({row}, {column})')
    return item


def row_of(table: Any, tier_id: str) -> int:
    for row in range(table.rowCount()):
        if cell(table, row, ID).text() == tier_id:
            return row
    raise SystemExit(f'SETTINGS FAIL: no Tier {tier_id!r} in the table')


def labels(db: Any) -> dict[str, str]:
    return {tier.id: tier.label for tier in config_admin(db).tier_config().tiers}


def open_library(path: str) -> Any:
    """A fresh library whose first-run column offers are already answered."""
    db = open_db(path)
    app = tier_list(db)
    app.mark_tier_column_offered()
    app.mark_read_column_offered()
    return db


def check_menu(path: str) -> None:
    """The menu ends with Settings…, and that item opens the dialog for this library."""
    db = open_library(path)
    try:
        gui = FakeGui(db, [])
        action = load_action(gui)
        items = action.tier_menu._menu.actions()
        found = [item for item in items if item.text() == ITEM]
        expect(len(found) == 1, [item.text() for item in items])
        expect(items[-1] is found[0], f'{ITEM} is not the last item')
        expect(items[-2].isSeparator(), f'no separator above {ITEM}')
        original = action_module.SettingsDialog
        action_module.SettingsDialog = FakeDialog
        try:
            found[0].trigger()
        finally:
            action_module.SettingsDialog = original
        expect(len(OPENED) == 1 and OPENED[0].gui is gui, 'the item did not open the dialog')
    finally:
        db.close()


def check_ok(path: str) -> None:
    """Two tabs, and OK saves as Customize does: prefs, saved searches, Tier menu."""
    seed = open_db(path)
    seed.create_custom_column('tier', 'Tier', 'text', False)
    seed.close()
    db = open_library(path)
    try:
        gui = FakeGui(db, [])
        action = load_action(gui)
        gui.iactions = {'Tier List': action}
        dialog = SettingsDialog(gui)
        widget = dialog.widget
        expect([widget.tabText(index) for index in range(widget.count())] == ['Tiers', 'Page', 'Backup'], 'tabs')
        backup: Any = widget.backup
        texts = {button.text() for button in backup.findChildren(QPushButton)}
        expect(texts == {'Import JSON…', 'Export JSON…'}, f'the Backup tab holds {sorted(texts)}')
        page: Any = widget.page
        page.theme.setCurrentIndex(page.theme.findData('light'))

        table = widget.tiers.table
        expect(len(table.tiers()) == 6, f'the Tiers tab shows {len(table.tiers())} Tiers')
        cell(table, row_of(table, 's'), LABEL).setText('Top')
        expect(labels(db)['s'] == 'S', 'editing the widget changed the stored config before OK')
        dialog.accept()
        expect(labels(db)['s'] == 'Top', f'OK did not store the label: {labels(db)}')
        expect(config_admin(db).page_defaults().theme == 'light', 'OK did not store the Page Defaults')
        expect('Tier Top' in db.new_api.saved_search_names(), sorted(db.new_api.saved_search_names()))
        shown = [item.text() for item in action.tier_menu._submenu.actions()]
        expect('Top' in shown, f'OK did not rebuild the Tier menu: {shown}')
    finally:
        db.close()


def check_cancel(path: str) -> None:
    """Cancel saves nothing."""
    db = open_library(path)
    try:
        dialog = SettingsDialog(FakeGui(db, []))
        table = dialog.widget.tiers.table
        cell(table, row_of(table, 'a'), LABEL).setText('Gone')
        dialog.reject()
        expect(labels(db)['a'] == 'A', f'Cancel saved something: {labels(db)}')
    finally:
        db.close()


def main() -> int:
    Application([])
    with tempfile.TemporaryDirectory() as tmp:
        check_menu(tmp + '/menu')
        check_ok(tmp + '/ok')
        check_cancel(tmp + '/cancel')
    print('SETTINGS OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())

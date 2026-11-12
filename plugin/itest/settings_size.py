"""Integration test for the Settings dialog's size: roomy by default, remembered once resized.

Run with ``calibre-debug -e plugin/itest/settings_size.py`` after installing the plugin into a
throwaway ``CALIBRE_CONFIG_DIRECTORY``. Prints ``SETTINGS SIZE OK`` and exits 0 on success.
calibre runs Python with -OO, which strips ``assert``; use ``expect``.
"""

import sys
import tempfile
from typing import Any

from calibre.gui2 import Application
from calibre.library import db as open_db
from calibre_plugins.tierlist.calibre_ui.adapters import tier_list
from calibre_plugins.tierlist.calibre_ui.settings_dialog import DEFAULT_SIZE, SettingsDialog
from fake_gui import FakeGui

RESIZED = (701, 655)


def expect(ok: bool, message: object) -> None:
    if not ok:
        raise SystemExit(f'SETTINGS SIZE FAIL: {message}')


def open_library(path: str) -> Any:
    db = open_db(path)
    app = tier_list(db)
    app.mark_tier_column_offered()
    app.mark_read_column_offered()
    return db


def shown(gui: Any, tab: str | None = None) -> SettingsDialog:
    dialog = SettingsDialog(gui, tab=tab)
    dialog.show()
    Application.processEvents()
    return dialog


def check_default(gui: Any) -> None:
    """With nothing saved, Settings and the Arrange board open at the default, cut to 90% of the screen."""
    for tab in (None, 'arrange'):
        dialog = shown(gui, tab)
        screen = dialog.screen()
        if screen is None:
            raise SystemExit(f'SETTINGS SIZE FAIL: {tab}: the dialog has no screen')
        room = screen.availableGeometry().size() * 0.9
        want = DEFAULT_SIZE.boundedTo(room)
        got = dialog.size()
        expect(got == want, f'{tab}: opened at {got.width()}x{got.height()}, want {want.width()}x{want.height()}')
        dialog.reject()


def check_remembered(gui: Any) -> None:
    """A size the user picks survives closing the dialog, by OK or Cancel."""
    dialog = shown(gui)
    dialog.resize(*RESIZED)
    Application.processEvents()
    dialog.reject()
    again = shown(gui, 'arrange')
    size = (again.size().width(), again.size().height())
    expect(size == RESIZED, f'reopened at {size}, not the {RESIZED} the user left')
    again.reject()


def main() -> int:
    Application([])
    with tempfile.TemporaryDirectory() as tmp:
        db = open_library(tmp + '/size')
        try:
            gui = FakeGui(db, [])
            check_default(gui)
            check_remembered(gui)
        finally:
            db.close()
    print('SETTINGS SIZE OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())

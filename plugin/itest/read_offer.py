"""Integration test for the Read State column offer and the Set up read column item.

Run with ``calibre-debug -e plugin/itest/read_offer.py`` after installing
``dist/tierlist.zip`` with ``calibre-customize -a`` into a throwaway
``CALIBRE_CONFIG_DIRECTORY``. Prints ``READ OFFER OK`` and exits 0 on success.

The dialog and column creation are stubbed: offscreen Qt cannot click a modal
dialog, and creating a column needs calibre's real main window.

calibre runs Python with -OO, which strips ``assert``; use ``expect``.
"""

import sys
import tempfile
from typing import Any

from calibre.gui2 import Application
from calibre.library import db as open_db
from calibre_plugins.tierlist.calibre_ui import column
from calibre_plugins.tierlist.calibre_ui.adapters import tier_list
from fake_gui import FakeGui, load_action

NEW = 'A new "Date read" column'


class Stubs:
    """Stands in for the dialog, the restart check, and column creation."""

    def __init__(self, choice: int | None, must_restart: bool = False) -> None:
        self.choice, self.restart = choice, must_restart
        self.shown: list[list[str]] = []
        self.created: list[tuple[str, str, str]] = []
        stubs = self

        class Dialog:
            @staticmethod
            def getItem(_gui: Any, _title: str, _label: str, items: list[str], *_: Any) -> tuple[str, bool]:
                stubs.shown.append(list(items))
                return ('', False) if stubs.choice is None else (items[stubs.choice], True)

        class Creator:
            def __init__(self, _gui: Any) -> None:
                pass

            def must_restart(self) -> bool:
                return stubs.restart

        column.QInputDialog, column.CreateNewCustomColumn = Dialog, Creator
        column.create_column = self.create

    def create(self, _gui: Any, lookup: str, heading: str, datatype: str) -> bool:
        self.created.append((lookup, heading, datatype))
        return True


def expect(ok: bool, message: object) -> None:
    if not ok:
        raise SystemExit(f'READ OFFER FAIL: {message}')


def library(path: str, *columns: tuple[str, str, str]) -> Any:
    db = open_db(path)
    for lookup, heading, datatype in columns:
        db.create_custom_column(lookup, heading, datatype, False)
    db.close()
    return open_db(path)


def check_offer(tmp: str) -> None:
    db = library(tmp + '/mapped', ('read', 'Read', 'bool'), ('tier', 'Tier', 'text'))
    gui, app = FakeGui(db, []), tier_list(db)
    stubs = Stubs(choice=1, must_restart=True)
    expect(not column.offer_read_column(gui, app), 'offered while a restart is pending')
    expect(not stubs.shown and not app.read_column_offered(), 'a pending restart burned the offer')
    stubs.restart = False
    expect(not column.offer_read_column(gui, app), 'mapping an existing column asked for a restart')
    expect(stubs.shown == [[NEW, 'Read (#read)']], stubs.shown)
    expect(app.read_column_ready() and app.tier_config().read_column == '#read', 'the choice was not mapped')
    expect(not column.offer_read_column(gui, app) and len(stubs.shown) == 1, 'offered twice')
    db.close()

    db = library(tmp + '/fresh', ('tier', 'Tier', 'text'))
    gui, app = FakeGui(db, []), tier_list(db)
    stubs = Stubs(choice=None)
    expect(not column.offer_read_column(gui, app), 'cancel reported a new column')
    expect(app.read_column_offered() and not stubs.created, 'cancel did not record the offer')
    stubs.choice = 0
    expect(column.offer_read_column(gui, app, force=True), 'creating the column did not ask for a restart')
    expect(stubs.created == [('#date_read', 'Date read', 'datetime')], stubs.created)
    db.close()


def check_setup_item(tmp: str) -> None:
    db = library(tmp + '/setup', ('tier', 'Tier', 'text'))
    app = tier_list(db)
    app.mark_tier_column_offered()
    app.mark_read_column_offered()
    gui = FakeGui(db, [])
    action = load_action(gui)
    texts = [a.text() for a in action.qaction.menu().actions()]
    expect('This library has no read column' in texts, texts)
    Stubs(choice=0)
    action.setup_read_column()
    texts = [a.text() for a in action.qaction.menu().actions()]
    expect('Restart calibre to finish adding the read column' in texts, texts)
    db.close()


def main() -> int:
    Application([])
    with tempfile.TemporaryDirectory() as tmp:
        check_offer(tmp)
        check_setup_item(tmp)
    print('READ OFFER OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())

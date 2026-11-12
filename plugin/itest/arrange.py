"""Integration test for the Arrange View: a staged drag saved by OK writes prefs and the Tier column.

Run with ``calibre-debug -e plugin/itest/arrange.py`` after installing the plugin into a
throwaway ``CALIBRE_CONFIG_DIRECTORY``. Prints ``ARRANGE OK`` and exits 0; Cancel writes nothing.
calibre runs Python with -OO, which strips ``assert``; use ``expect``.
"""

import sys
import tempfile
from typing import Any

from calibre.ebooks.metadata.book.base import Metadata
from calibre.gui2 import Application
from calibre.library import db as open_db
from calibre_plugins.tierlist.calibre_ui import action as action_module
from calibre_plugins.tierlist.calibre_ui.adapters import tier_list
from calibre_plugins.tierlist.calibre_ui.settings_dialog import SettingsDialog
from calibre_plugins.tierlist.compile import CompileRequest
from calibre_plugins.tierlist.lane_order import LANE_ORDER_KEY
from fake_gui import FakeGui, load_action

COLUMNS = (('tier', 'Tier', 'text'), ('date_read', 'Date read', 'datetime'))
PREF_NS = 'tierlist'
ITEMS = ('Arrange board…', 'Settings…')
OPENED: list[Any] = []


def expect(ok: bool, message: object) -> None:
    if not ok:
        raise SystemExit(f'ARRANGE FAIL: {message}')


def book(db: Any, title: str, series: str | None = None, index: float | None = None) -> int:
    metadata = Metadata(title, ['Author'])
    metadata.series, metadata.series_index = series, index
    return int(db.new_api.create_book_entry(metadata))


def library(path: str) -> tuple[Any, int, int, int]:
    """A library with a Dune series, a Solo card, and an Other card, all in Tier S and read."""
    seed = open_db(path)
    for lookup, heading, datatype in COLUMNS:
        seed.create_custom_column(lookup, heading, datatype, False)
    seed.close()
    db = open_db(path)
    first = book(db, 'Dune', 'Dune', 1.0)
    second = book(db, 'Dune Messiah', 'Dune', 2.0)
    solo = book(db, 'Solo')
    other = book(db, 'Other')
    tier_list(db).set_book_tier([first, second, solo, other], 's')
    return db, solo, other, first


class FakeDialog:
    """Stands in for SettingsDialog, recording the tab the menu asked for."""

    def __init__(self, gui: Any, tab: str | None = None) -> None:
        self.gui, self.tab = gui, tab
        OPENED.append(self)

    def exec(self) -> int:
        return 0


def check_menu(path: str) -> None:
    """TierMenu ends with Arrange board… and Settings…, and Arrange opens Settings on its tab."""
    db, _, _, _ = library(path)
    try:
        tier_list(db).mark_tier_column_offered()
        tier_list(db).mark_read_column_offered()
        gui = FakeGui(db, [])
        action = load_action(gui)
        items = action.tier_menu._menu.actions()
        expect([item.text() for item in items[-2:]] == list(ITEMS), [item.text() for item in items])
        expect(items[-3].isSeparator(), 'no separator above Arrange board…')
        original = action_module.SettingsDialog
        action_module.SettingsDialog = FakeDialog
        try:
            items[-2].trigger()
        finally:
            action_module.SettingsDialog = original
        expect(len(OPENED) == 1 and OPENED[0].tab == 'arrange', OPENED)
    finally:
        db.close()


def lane_items(data: Any, tier: str) -> list[tuple[str, object]]:
    lane = next(lane for lane in data.lanes if lane.tier == tier)
    return [('series', item.stack) if item.stack is not None else ('book', item.card) for item in lane.items]


def stored_order(db: Any) -> Any:
    return db.prefs.get_namespaced(PREF_NS, LANE_ORDER_KEY, None)


def check_saving(path: str) -> None:
    db, solo, other, _ = library(path)
    try:
        app = tier_list(db)
        dialog = SettingsDialog(FakeGui(db, []), tab='arrange')
        expect(dialog.widget.tabText(dialog.widget.currentIndex()) == 'Arrange', 'Settings did not open on Arrange')
        tab: Any = dialog.widget.arrange
        tab.drop('series', 'Dune', 'a', 0)
        tab.drop('book', solo, 'b', 0)
        expect(app.series_tier_overrides() == {}, 'the staged drag wrote the Override before OK')
        expect(db.new_api.field_for('#tier', solo) == 's', 'the staged drag wrote the Book Tier before OK')
        expect(stored_order(db) is None, 'the staged drag wrote Lane Order before OK')
        dialog.accept()
        overrides = app.series_tier_overrides()
        expect(overrides == {'Dune': 'a'}, f'OK did not write the Override: {overrides}')
        expect(db.new_api.field_for('#tier', solo) == 'b', 'OK did not write the Book Tier')
        order = stored_order(db)
        expect(order == {'s': [{'book': other}], 'a': [{'series': 'Dune'}], 'b': [{'book': solo}]}, order)
        ids = tuple(sorted(db.new_api.all_book_ids()))
        data = app.compile(CompileRequest('library', ids, 'Lib', '0.1.0'))
        expect(lane_items(data, 'a') == [('series', 'Dune')], lane_items(data, 'a'))
        expect(lane_items(data, 's') == [('book', other)], lane_items(data, 's'))
        expect(lane_items(data, 'b') == [('book', solo)], lane_items(data, 'b'))
    finally:
        db.close()


def check_cancel(path: str) -> None:
    db, solo, _, _ = library(path)
    try:
        app = tier_list(db)
        dialog = SettingsDialog(FakeGui(db, []), tab='arrange')
        tab: Any = dialog.widget.arrange
        tab.drop('series', 'Dune', 'b', 0)
        dialog.reject()
        expect(app.series_tier_overrides() == {}, f'Cancel wrote the Override: {app.series_tier_overrides()}')
        expect(db.new_api.field_for('#tier', solo) == 's', 'Cancel wrote the Book Tier')
        expect(stored_order(db) is None, 'Cancel wrote Lane Order')
    finally:
        db.close()


def main() -> int:
    Application([])
    with tempfile.TemporaryDirectory() as tmp:
        check_menu(tmp + '/menu')
        check_saving(tmp + '/saving')
        check_cancel(tmp + '/cancel')
    print('ARRANGE OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())

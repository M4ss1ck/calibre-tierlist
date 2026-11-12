"""Integration test for Settings Export: one library's settings import into a second.

Run with ``calibre-debug -e plugin/itest/settings_export.py`` after installing the plugin into a
throwaway ``CALIBRE_CONFIG_DIRECTORY``. Prints ``SETTINGS EXPORT OK`` and exits 0 on success.
The file and message box dialogs are stubbed: offscreen Qt cannot click a modal dialog.
calibre runs Python with -OO, which strips ``assert``; use ``expect``.
"""

import sys
import tempfile
from typing import Any, ClassVar

from calibre.ebooks.metadata.book.base import Metadata
from calibre.gui2 import Application
from calibre.library import db as open_db
from calibre_plugins.tierlist.calibre_ui import config_io
from calibre_plugins.tierlist.calibre_ui.adapters import config_admin, tier_list
from calibre_plugins.tierlist.calibre_ui.config_widget import ConfigWidget
from calibre_plugins.tierlist.lane_order import LANE_ORDER_KEY
from calibre_plugins.tierlist.page_defaults import PageDefaults
from fake_gui import FakeGui

PREF_NS = 'tierlist'
ORDER = {'s': [{'series': 'Earthsea'}], 'a': [{'series': 'Dune'}]}


def expect(ok: bool, message: object) -> None:
    if not ok:
        raise SystemExit(f'SETTINGS EXPORT FAIL: {message}')


class Dialog:
    """Stands in for QFileDialog, returning the one path the test picked."""

    path = ''

    @classmethod
    def getOpenFileName(cls, _parent: Any, _caption: str, _directory: str, _filter: str) -> tuple[str, str]:
        return cls.path, ''

    @classmethod
    def getSaveFileName(cls, _parent: Any, _caption: str, _directory: str, _filter: str) -> tuple[str, str]:
        return cls.path, ''


class Answer:
    """Stands in for QMessageBox, answering Yes and recording each question."""

    class StandardButton:
        Yes = 'yes'
        No = 'no'

    asked: ClassVar[list[str]] = []

    @classmethod
    def question(cls, _parent: Any, _title: str, text: str) -> str:
        cls.asked.append(text)
        return cls.StandardButton.Yes


def book(db: Any, title: str, series: str | None = None, index: float | None = None) -> int:
    metadata = Metadata(title, ['Author'])
    metadata.series, metadata.series_index = series, index
    return int(db.new_api.create_book_entry(metadata))


def library(path: str) -> Any:
    """A fresh library with a Tier and Read column, and the two series Lane Order names."""
    seed = open_db(path)
    seed.create_custom_column('tier', 'Tier', 'text', False)
    seed.create_custom_column('date_read', 'Date read', 'datetime', False)
    seed.close()
    db = open_db(path)
    dune = book(db, 'Dune', 'Dune', 1.0)
    book(db, 'Dune Messiah', 'Dune', 2.0)
    earthsea = book(db, 'A Wizard of Earthsea', 'Earthsea', 1.0)
    tier_list(db).set_book_tier([dune, earthsea], 's')
    return db


def first_library(db: Any) -> None:
    """A library with Page Defaults, an Override, and Lane Order."""
    app = tier_list(db)
    dune = next(book_id for book_id in db.new_api.all_book_ids() if db.new_api.field_for('title', book_id) == 'Dune')
    app.set_series_tier([dune], 'a')
    config_admin(db).save_page_defaults(PageDefaults(theme='light', title='My shelf'))
    db.prefs.set_namespaced(PREF_NS, LANE_ORDER_KEY, ORDER)


def widget_for(db: Any) -> Any:
    config_io.QFileDialog, config_io.QMessageBox = Dialog, Answer
    return ConfigWidget(FakeGui(db, []))


def export_settings(db: Any, path: str) -> None:
    widget = widget_for(db)
    cell(widget.tiers.table, row_of(widget.tiers.table, 's'), 1).setText('Top')
    widget.backup.include.setChecked(True)
    Dialog.path = path
    widget.backup.export_json()


def cell(table: Any, row: int, column: int) -> Any:
    item = table.item(row, column)
    expect(item is not None, f'no cell at ({row}, {column})')
    return item


def row_of(table: Any, tier_id: str) -> int:
    for row in range(table.rowCount()):
        if cell(table, row, 0).text() == tier_id:
            return row
    raise SystemExit(f'SETTINGS EXPORT FAIL: no Tier {tier_id!r}')


def check_round_trip(tmp: str) -> None:
    path = tmp + '/settings.json'
    source = library(tmp + '/source')
    try:
        first_library(source)
        export_settings(source, path)
    finally:
        source.close()
    target = library(tmp + '/target')
    try:
        widget = widget_for(target)
        Dialog.path = path
        widget.backup.import_json()
        expect(bool(Answer.asked) and 'series override' in Answer.asked[-1], Answer.asked)
        widget.save()
        labels = {tier.id: tier.label for tier in config_admin(target).tier_config().tiers}
        expect(labels.get('s') == 'Top', f'Tiers did not carry over: {labels}')
        defaults = config_admin(target).page_defaults()
        expect((defaults.theme, defaults.title) == ('light', 'My shelf'), defaults)
        expect(tier_list(target).series_tier_overrides() == {'Dune': 'a'}, 'Overrides')
        expect(target.prefs.get_namespaced(PREF_NS, LANE_ORDER_KEY, None) == ORDER, 'Lane Order')
    finally:
        target.close()


def main() -> int:
    Application([])
    with tempfile.TemporaryDirectory() as tmp:
        check_round_trip(tmp)
    print('SETTINGS EXPORT OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())

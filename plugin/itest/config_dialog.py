"""Integration test for the Tier Config dialog: the Tier table, column mapping, and saved settings.

Run with ``calibre-debug -e plugin/itest/config_dialog.py`` after installing
``dist/tierlist.zip`` with ``calibre-customize -a`` into a throwaway
``CALIBRE_CONFIG_DIRECTORY``. Prints ``CONFIG DIALOG OK`` and exits 0 on success.
The message box and error dialog are stubbed: offscreen Qt cannot click a modal
dialog; the widget itself is driven through its public methods and slots.

calibre runs Python with -OO, which strips ``assert``; use ``expect``.
"""

import sys
import tempfile
from dataclasses import replace
from datetime import datetime
from typing import Any, ClassVar

from calibre.ebooks.metadata.book.base import Metadata
from calibre.gui2 import Application
from calibre.library import db as open_db
from calibre.utils.date import local_tz
from calibre_plugins.tierlist.calibre_ui import config_io, config_widget
from calibre_plugins.tierlist.calibre_ui.adapters import config_admin
from calibre_plugins.tierlist.calibre_ui.config_widget import ConfigWidget
from calibre_plugins.tierlist.tiers import DEFAULT_TIER_CONFIG
from fake_gui import FakeGui

ID, LABEL = 0, 1
COLUMNS = (('tier', 'Tier', 'text'), ('date_read', 'Date read', 'datetime'), ('total', 'Total', 'int'))


def expect(ok: bool, message: object) -> None:
    if not ok:
        raise SystemExit(f'CONFIG DIALOG FAIL: {message}')


class YesBox:
    """Stands in for QMessageBox, answering Yes and recording each question."""

    class StandardButton:
        Yes = 'yes'

    asked: ClassVar[list[str]] = []

    @classmethod
    def question(cls, _parent: Any, _title: str, text: str) -> str:
        cls.asked.append(text)
        return cls.StandardButton.Yes


class ErrorDialog:
    """Stands in for calibre's error dialog, recording each message."""

    shown: ClassVar[list[str]] = []

    def __call__(self, _parent: Any, _title: str, message: str, *_args: Any, **_kwargs: Any) -> None:
        self.shown.append(message)


def widget_for(db: Any) -> Any:
    config_io.QMessageBox, config_widget.error_dialog = YesBox, ErrorDialog()
    return ConfigWidget(FakeGui(db, []))


def cell(table: Any, row: int, column: int) -> Any:
    item = table.item(row, column)
    expect(item is not None, f'no cell at ({row}, {column})')
    return item


def row_of(table: Any, tier_id: str) -> int:
    for row in range(table.rowCount()):
        if cell(table, row, ID).text() == tier_id:
            return row
    raise SystemExit(f'CONFIG DIALOG FAIL: no Tier {tier_id!r} in the table')


def check_fresh(tmp: str) -> None:
    db = open_db(tmp + '/fresh')
    try:
        widget = widget_for(db)
        expect(len(widget.table.tiers()) == 6, f'fresh library shows {len(widget.table.tiers())} Tiers')
        expect(widget.build_config() == DEFAULT_TIER_CONFIG, f'fresh config: {widget.build_config()}')
        expect(widget.tier_column.currentData() == '#tier', f'tier column {widget.tier_column.currentData()!r}')
        expect(widget.read_column.currentData() == '#date_read', f'read column {widget.read_column.currentData()!r}')
        expect(widget.total_column.currentData() == '', f'total column {widget.total_column.currentData()!r}')
    finally:
        db.close()


def check_mapped(tmp: str) -> None:
    seed = open_db(tmp + '/mapped')
    for lookup, heading, datatype in COLUMNS:
        seed.create_custom_column(lookup, heading, datatype, False)
    seed.close()
    db = open_db(tmp + '/mapped')
    try:
        book = db.new_api.create_book_entry(Metadata('Book', ['Author']))
        read = datetime(2021, 4, 5, 12, tzinfo=local_tz)
        db.new_api.set_field('#tier', {book: 'f'})
        db.new_api.set_field('#date_read', {book: read})
        stored = replace(
            config_admin(db).tier_config(), tier_column='#tier', read_column='#date_read', series_total_column='#total'
        )
        config_admin(db).save(stored)

        widget = widget_for(db)
        expect(widget.tier_column.currentData() == '#tier', 'the Tier column was not preselected')
        expect(widget.read_column.currentData() == '#date_read', 'the Read column was not preselected')
        expect(widget.total_column.currentData() == '#total', 'the Series total column was not preselected')

        table = widget.table
        cell(table, row_of(table, 's'), LABEL).setText('Top')
        expect(widget.validate(), 'a valid Tier Config was rejected')
        widget.save()
        labels = {tier.id: tier.label for tier in config_admin(db).tier_config().tiers}
        expect(labels['s'] == 'Top', f'the label was not stored: {labels}')
        found = list(db.new_api.saved_search_names())
        expect('Tier Top' in found and 'Tier S' not in found, f'renaming left {sorted(found)}')
        expect(db.new_api.field_for('#tier', book) == 'f', 'renaming a Tier changed the book')

        cell(table, row_of(table, 's'), LABEL).setText('')
        expect(not widget.validate(), 'an empty label validated')
        expect('label' in ErrorDialog.shown[-1], ErrorDialog.shown)
        cell(table, row_of(table, 's'), LABEL).setText('Top')

        table.selectRow(row_of(table, 'f'))
        widget.remove_tier()
        expect('f' not in {tier.id for tier in table.tiers()}, 'the removed Tier stayed in the table')
        expect('1 book holds this Tier' in YesBox.asked[-1], YesBox.asked)
        widget.save()
        expect(db.new_api.field_for('#tier', book) is None, 'the removed Tier kept its book')
        kept = db.new_api.field_for('#date_read', book)
        expect(kept is not None and kept.astimezone(local_tz).date() == read.date(), f'read date changed: {kept}')
        expect('Tier F' not in db.new_api.saved_search_names(), sorted(db.new_api.saved_search_names()))
    finally:
        db.close()


def main() -> int:
    Application([])
    with tempfile.TemporaryDirectory() as tmp:
        check_fresh(tmp)
        check_mapped(tmp)
    print('CONFIG DIALOG OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())

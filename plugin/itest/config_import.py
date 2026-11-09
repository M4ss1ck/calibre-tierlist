"""Integration test for Tier Config import: an import that drops Tiers books hold asks first.

Run with ``calibre-debug -e plugin/itest/config_import.py`` after installing
``dist/tierlist.zip`` with ``calibre-customize -a`` into a throwaway
``CALIBRE_CONFIG_DIRECTORY``. Prints ``CONFIG IMPORT OK`` and exits 0 on success.
The file dialog and message box are stubbed: offscreen Qt cannot click a modal
dialog; the widget itself is driven through its public methods and slots.

calibre runs Python with -OO, which strips ``assert``; use ``expect``.
"""

import json
import sys
import tempfile
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Any

from calibre.ebooks.metadata.book.base import Metadata
from calibre.gui2 import Application
from calibre.library import db as open_db
from calibre.utils.date import local_tz
from calibre_plugins.tierlist.calibre_ui import config_io
from calibre_plugins.tierlist.calibre_ui.adapters import config_admin
from calibre_plugins.tierlist.calibre_ui.config_widget import ConfigWidget
from fake_gui import FakeGui

DEFAULT_IDS = {'s', 'a', 'b', 'c', 'd', 'f'}


def expect(ok: bool, message: object) -> None:
    if not ok:
        raise SystemExit(f'CONFIG IMPORT FAIL: {message}')


class Answer:
    """Stands in for QMessageBox, giving one answer and recording each question."""

    class StandardButton:
        Yes = 'yes'
        No = 'no'

    def __init__(self, answer: str) -> None:
        self.answer = answer
        self.asked: list[str] = []

    def question(self, _parent: Any, _title: str, text: str) -> str:
        self.asked.append(text)
        return self.answer


class OpenDialog:
    """Stands in for QFileDialog, returning the path the test picked."""

    path = ''

    @staticmethod
    def getOpenFileName(_parent: Any, _caption: str, _directory: str, _filter: str) -> tuple[str, str]:
        return OpenDialog.path, ''


def open_library(tmp: str) -> Any:
    path = tmp + '/import'
    db = open_db(path)
    db.create_custom_column('tier', 'Tier', 'text', False)
    db.create_custom_column('date_read', 'Date read', 'datetime', False)
    db.close()
    return open_db(path)


def incoming(stored: Any) -> Any:
    """The stored config without 'f', with 's' renamed to 'Top' and other column names: the import the test feeds."""
    tiers = tuple(replace(tier, label='Top') if tier.id == 's' else tier for tier in stored.tiers if tier.id != 'f')
    return replace(stored, tiers=tiers, tier_column='#rank', read_column='#read', series_total_column='#total')


def check_import(tmp: str) -> None:
    db = open_library(tmp)
    try:
        book = db.new_api.create_book_entry(Metadata('Book', ['Author']))
        db.new_api.set_field('#tier', {book: 'f'})
        db.new_api.set_field('#date_read', {book: datetime(2021, 4, 5, 12, tzinfo=local_tz)})
        path = Path(tmp + '/config.json')
        path.write_text(json.dumps(incoming(config_admin(db).tier_config()).to_dict()), encoding='utf-8')
        config_io.QFileDialog = OpenDialog
        OpenDialog.path = str(path)

        widget = ConfigWidget(FakeGui(db, []))
        expect({tier.id for tier in widget.table.tiers()} == DEFAULT_IDS, 'the widget did not start on the defaults')

        no = Answer(Answer.StandardButton.No)
        config_io.QMessageBox = no
        widget.import_json()
        expect(bool(no.asked) and '1 book holds a Tier this import removes' in no.asked[-1], no.asked)
        expect({tier.id for tier in widget.table.tiers()} == DEFAULT_IDS, 'declining the import changed the table')
        expect({tier.id: tier.label for tier in widget.table.tiers()}['s'] == 'S', 'declining renamed a Tier')

        yes = Answer(Answer.StandardButton.Yes)
        config_io.QMessageBox = yes
        widget.import_json()
        expect(len(yes.asked) == 1, yes.asked)
        labels = {tier.id: tier.label for tier in widget.table.tiers()}
        expect('f' not in labels and labels['s'] == 'Top', f'the import did not load: {labels}')
        expect(widget.tier_column.currentData() == '#tier', 'the import changed the Tier column')
        expect(widget.read_column.currentData() == '#date_read', 'the import changed the Read column')
        expect(widget.total_column.currentData() == '', 'the import changed the Series total column')
        expect(db.new_api.field_for('#tier', book) == 'f', 'the import touched the book before save')
    finally:
        db.close()


def main() -> int:
    Application([])
    with tempfile.TemporaryDirectory() as tmp:
        check_import(tmp)
    print('CONFIG IMPORT OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())

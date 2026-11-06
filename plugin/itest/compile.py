"""Integration test for the Compile dialog, the Compile Scopes, and the HTML output.

Run with ``calibre-debug -e plugin/itest/compile.py`` after installing
``dist/tierlist.zip`` with ``calibre-customize -a`` into a throwaway
``CALIBRE_CONFIG_DIRECTORY``. Prints ``COMPILE OK`` and exits 0 on success.

calibre runs Python with -OO, which strips ``assert``; use ``expect``.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from calibre.ebooks.metadata.book.base import Metadata
from calibre.gui2 import Application
from calibre.library import db as open_db
from calibre_plugins.tierlist.app import TierList
from calibre_plugins.tierlist.calibre_ui import compile_job
from calibre_plugins.tierlist.calibre_ui.adapters import tier_list
from calibre_plugins.tierlist.calibre_ui.compile_dialog import CompileDialog
from calibre_plugins.tierlist.calibre_ui.compile_job import run_compile, scope_book_ids, start_compile
from calibre_plugins.tierlist.compile import CompileRequest
from fake_gui import FakeGui
from fake_job import FakeJobAction
from qt.core import QDialog

TITLES = ('Alpha', 'Bravo', 'The </script> Problem', 'Unread')
REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / 'dist' / 'itest' / 'compiled.html'
JOB_OUTPUT = REPO / 'dist' / 'itest' / 'job.html'
TEMPLATE = REPO / 'web' / 'dist' / 'template.html'


def expect(ok: bool, message: object) -> None:
    if not ok:
        raise SystemExit(f'COMPILE FAIL: {message}')


def library(path: str) -> Any:
    db = open_db(path)
    db.create_custom_column('tier', 'Tier', 'text', False)
    db.create_custom_column('date_read', 'Date read', 'datetime', False)
    db.close()
    return open_db(path)


def compiling_library(path: str) -> tuple[Any, list[int], TierList]:
    db = library(path)
    ids = [db.new_api.create_book_entry(Metadata(title, ['Author'])) for title in TITLES]
    app: TierList = tier_list(db)
    app.set_book_tier(ids[:3], 'a')
    app.clear_book_tier([ids[1]])
    return db, ids, app


def check_scopes(db: Any, ids: list[int]) -> None:
    expect(scope_book_ids(FakeGui(db, []), 'library') == tuple(sorted(ids)), 'library scope missed books')
    picked = [ids[2], ids[0]]
    expect(scope_book_ids(FakeGui(db, picked), 'selection') == tuple(sorted(picked)), 'selection scope was wrong')
    db.data.set_base_restriction('title:"=Alpha"')
    db.data.set_base_restriction_name('Only Alpha')
    try:
        expect(scope_book_ids(FakeGui(db, []), 'virtual_library') == (ids[0],), 'virtual library scope was wrong')
    finally:
        db.data.set_base_restriction('')
        db.data.set_base_restriction_name('')


def check_dialog(db: Any, app: TierList) -> None:
    gui = FakeGui(db, [])
    dialog = CompileDialog(gui, db, app)
    expect(dialog.scope() == 'library', dialog.scope())
    expect(not dialog.virtual_radio.isEnabled(), 'virtual library offered when none is active')
    expect(dialog.path_edit.text() == app.output_path(), dialog.path_edit.text())
    dialog.path_edit.setText('   ')
    dialog.accept()
    expect(dialog.result() != QDialog.DialogCode.Accepted, 'a blank output path closed the dialog')


def check_compile(db: Any, ids: list[int], app: TierList) -> None:
    request = CompileRequest('library', tuple(sorted(ids)), os.path.basename(db.library_path), '0.1.0')
    lines: list[str] = []
    written = run_compile(app, request, TEMPLATE.read_text(encoding='utf-8'), str(OUTPUT), lines.append)
    expect(written == str(OUTPUT), written)
    expect(OUTPUT.is_file(), f'no compiled file at {OUTPUT}')
    html = OUTPUT.read_text(encoding='utf-8')
    expect('Alpha' in html, 'Alpha missing from the compiled HTML')
    expect('__TIERLIST_DATA__' not in html, 'the template marker survived')
    expect(len(lines) == 1 and lines[0].startswith('Tier List compiled: 3 of 4 books'), lines)
    expect('</script> Problem' not in html, 'the script-closing title was not escaped')


def check_job(db: Any, ids: list[int]) -> None:
    action = FakeJobAction(db)
    request = CompileRequest('library', tuple(sorted(ids)), os.path.basename(db.library_path), '0.1.0')
    opened: list[str] = []
    compile_job.open_local_file = opened.append
    start_compile(action, request, TEMPLATE.read_text(encoding='utf-8'), str(JOB_OUTPUT))
    expect(JOB_OUTPUT.is_file(), f'no compiled file at {JOB_OUTPUT}')
    expect(opened == [str(JOB_OUTPUT)], opened)
    expect(len(action.gui.status_bar.messages) == 1, action.gui.status_bar.messages)
    expect(action.gui.exceptions == [], action.gui.exceptions)
    expect(action.gui.job_manager.jobs[-1].failed is False, 'the compile job failed')


def main() -> int:
    Application([])
    with tempfile.TemporaryDirectory() as tmp:
        db, ids, app = compiling_library(tmp + '/compiled')
        try:
            check_dialog(db, app)
            check_scopes(db, ids)
            check_compile(db, ids, app)
            check_job(db, ids)
        finally:
            db.close()
    print('COMPILE OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())

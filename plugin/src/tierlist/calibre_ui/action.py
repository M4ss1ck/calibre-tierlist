"""The Tier List action: toolbar button and book list context menu entry."""

import os
from collections.abc import Callable
from typing import Any

from calibre.gui2 import error_dialog, gprefs
from calibre.gui2.actions import InterfaceAction
from qt.core import QDialog

from ..app import TierList
from ..compile import CompileRequest
from . import column
from .adapters import tier_list
from .compile_dialog import CompileDialog
from .compile_job import scope_book_ids, start_compile
from .menu import TierMenu

load_translations()

LAYOUTS = ('toolbar', 'context-menu')
CLAIMED_KEY = 'tierlist-layouts-claimed'


class TierListAction(InterfaceAction):
    name = 'Tier List'
    action_spec = ('Tier List', None, _('Compile a tier list of your series'), None)
    action_type = 'current'

    def genesis(self) -> None:
        self.column_created_paths: set[str] = set()
        self.read_column_created_paths: set[str] = set()
        self.tier_menu = TierMenu(self)
        self.qaction.triggered.connect(self.show_dialog)
        self.add_to_action_layouts()

    def initialization_complete(self) -> None:
        self.rebuild_menu()
        self.offer_tier_column(self.gui.current_db)
        self.offer_read_column(self.gui.current_db)

    def library_changed(self, db: Any) -> None:
        self.rebuild_menu(db)
        self.offer_tier_column(db)
        self.offer_read_column(db)

    def rebuild_menu(self, db: Any = None) -> None:
        self.tier_menu.rebuild(db)

    def offer_tier_column(self, db: Any) -> None:
        if column.offer_tier_column(self.gui, tier_list(db)):
            self.column_created_paths.add(db.library_path)

    def offer_read_column(self, db: Any) -> None:
        if column.offer_read_column(self.gui, tier_list(db)):
            self.read_column_created_paths.add(db.library_path)

    def create_tier_column(self) -> None:
        db = self.gui.current_db
        if column.create_tier_column(self.gui, tier_list(db).tier_config().tier_column):
            self.column_created_paths.add(db.library_path)

    def setup_read_column(self) -> None:
        db = self.gui.current_db
        if column.offer_read_column(self.gui, tier_list(db), force=True):
            self.read_column_created_paths.add(db.library_path)
        self.rebuild_menu()

    def send_to_tier(self, tier_id: str) -> None:
        self._on_selection(lambda app, ids: app.set_book_tier(ids, tier_id))

    def clear_tier(self) -> None:
        self._on_selection(TierList.clear_book_tier)

    def set_series_tier(self, tier_id: str, *_: Any) -> None:
        self._on_selection(lambda app, ids: app.set_series_tier(ids, tier_id))

    def clear_series_tier(self, *_: Any) -> None:
        self._on_selection(TierList.clear_series_tier)

    def mark_read(self) -> None:
        self._on_selection(TierList.mark_read)

    def mark_unread(self) -> None:
        self._on_selection(TierList.mark_unread)

    def _on_selection(self, use_case: Callable[[TierList, list[int]], None]) -> None:
        ids = self.gui.library_view.get_selected_ids()
        if not ids:
            return
        use_case(tier_list(self.gui.current_db), ids)
        self.gui.library_view.model().refresh_ids(ids)

    def show_dialog(self, *args: Any) -> None:
        db = self.gui.current_db
        app = tier_list(db)
        dialog = CompileDialog(self.gui, db, app)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        app.remember_output_path(dialog.path())
        template = self.load_resources(['template.html']).get('template.html')
        if template is None:
            error_dialog(
                self.gui,
                self.name,
                _('This plugin was built without the web template, so it cannot compile a tier list.'),
                show=True,
            )
            return
        scope = dialog.scope()
        request = CompileRequest(
            scope,
            scope_book_ids(self.gui, scope),
            os.path.basename(db.library_path),
            '.'.join(map(str, self.interface_action_base_plugin.version)),
        )
        start_compile(self, request, template.decode('utf-8'), dialog.path())

    def add_to_action_layouts(self) -> None:
        """calibre only offers new plugins a place in the layouts via its
        plugin preferences dialog, so claim our spot once, on first load.
        Never again: a user who removes the button must not get it back."""
        if gprefs.get(CLAIMED_KEY, False):
            return
        gprefs[CLAIMED_KEY] = True
        for location in LAYOUTS:
            key = f'action-layout-{location}'
            current = tuple(gprefs.get(key, ()))
            if self.name not in current:
                gprefs[key] = (*current, self.name)

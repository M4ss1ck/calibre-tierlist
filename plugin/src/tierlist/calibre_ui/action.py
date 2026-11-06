"""The Tier List action: toolbar button and book list context menu entry."""

from collections.abc import Callable
from typing import Any

from calibre.gui2 import gprefs, info_dialog
from calibre.gui2.actions import InterfaceAction

from ..app import TierList
from . import column
from .adapters import tier_list
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
            self.column_created_paths.add(db.library_path)

    def create_tier_column(self) -> None:
        db = self.gui.current_db
        if column.create_tier_column(self.gui, tier_list(db).tier_config().tier_column):
            self.column_created_paths.add(db.library_path)

    def setup_read_column(self) -> None:
        column.offer_read_column(self.gui, tier_list(self.gui.current_db), force=True)
        self.rebuild_menu()

    def send_to_tier(self, tier_id: str) -> None:
        self._on_selection(lambda app, ids: app.set_book_tier(ids, tier_id))

    def clear_tier(self) -> None:
        self._on_selection(TierList.clear_book_tier)

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
        info_dialog(self.gui, self.name, _('Coming soon'), show=True)

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

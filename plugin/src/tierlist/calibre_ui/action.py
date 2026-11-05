"""The Tier List action: toolbar button and book list context menu entry."""

from typing import Any

from calibre.gui2 import gprefs, info_dialog
from calibre.gui2.actions import InterfaceAction

load_translations()

LAYOUTS = ('toolbar', 'context-menu')
CLAIMED_KEY = 'tierlist-layouts-claimed'


class TierListAction(InterfaceAction):
    name = 'Tier List'
    action_spec = ('Tier List', None, _('Compile a tier list of your series'), None)
    action_type = 'current'

    def genesis(self) -> None:
        self.qaction.triggered.connect(self.show_dialog)
        self.add_to_action_layouts()

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

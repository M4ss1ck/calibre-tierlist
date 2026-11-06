"""The Tier List action's menu: Send to tier items, Clear tier, and Read State."""

from collections.abc import Iterable
from functools import partial
from typing import Any

from qt.core import QMenu

from ..tiers import Tier
from .adapters import tier_list


class TierMenu:
    """Builds and rebuilds the action's menu over the current library."""

    def __init__(self, action: Any) -> None:
        self._action = action
        self._created: list[Any] = []
        self._unregistered: list[Any] = []
        self._menu = QMenu()
        self._submenu = self._menu.addMenu(_('Send to tier'))
        self._menu.aboutToShow.connect(self.rebuild)
        action.qaction.setMenu(self._menu)

    def rebuild(self, db: Any = None) -> None:
        """Replace every item, re-registering its shortcut with calibre."""
        keyboard = self._action.gui.keyboard
        for created in self._created:
            # create_menu_action also adds each item to the gui, so clear() alone
            # would leave it alive, still holding the user's shortcut.
            keyboard.unregister_shortcut(created.calibre_shortcut_unique_name)
            self._action.gui.removeAction(created)
            self._menu.removeAction(created)
        self._created.clear()
        for added in self._unregistered:
            self._menu.removeAction(added)
        self._unregistered.clear()
        self._submenu.clear()
        if db is None:
            db = self._action.gui.current_db
        app = tier_list(db)
        if app.tier_column_ready():
            self._add_tiers(app.tier_config().tiers)
        else:
            self._add_missing(db)
        self._add_read_state(app, db)
        keyboard.finalize()

    def _add_tiers(self, tiers: Iterable[Tier]) -> None:
        for tier in tiers:
            self._register(
                self._submenu,
                f'send-to-tier-{tier.id}',
                tier.label,
                _('Send to tier: {}').format(tier.label),
                partial(self._send, tier.id),
            )
        self._submenu.addSeparator()
        self._register(self._submenu, 'clear-tier', _('Clear tier'), _('Clear tier'), self._clear)

    def _add_read_state(self, app: Any, db: Any) -> None:
        if app.read_column_ready():
            self._register(self._menu, 'mark-read', _('Mark read'), _('Mark read'), self._mark_read)
            self._register(self._menu, 'mark-unread', _('Mark unread'), _('Mark unread'), self._mark_unread)
        else:
            if db.library_path in self._action.read_column_created_paths:
                text = _('Restart calibre to finish adding the read column')
            else:
                text = _('This library has no read column')
            explanation = self._menu.addAction(text)
            explanation.setEnabled(False)
            self._unregistered.append(explanation)
            setup = self._menu.addAction(_('Set up read column…'), self._action.setup_read_column)
            self._unregistered.append(setup)

    def _send(self, tier_id: str, *_: Any) -> None:
        self._action.send_to_tier(tier_id)

    def _clear(self, *_: Any) -> None:
        self._action.clear_tier()

    def _mark_read(self, *_: Any) -> None:
        self._action.mark_read()

    def _mark_unread(self, *_: Any) -> None:
        self._action.mark_unread()

    def _add_missing(self, db: Any) -> None:
        if db.library_path in self._action.column_created_paths:
            text = _('Restart calibre to finish adding the tier column')
        else:
            text = _('This library has no tier column')
        explanation = self._submenu.addAction(text)
        explanation.setEnabled(False)
        self._submenu.addAction(_('Create tier column…'), self._action.create_tier_column)

    def _register(self, menu: Any, unique_name: str, text: str, shortcut_name: str, triggered: Any) -> None:
        created = self._action.create_menu_action(
            menu,
            unique_name,
            text,
            shortcut=None,
            shortcut_name=shortcut_name,
            triggered=triggered,
            persist_shortcut=True,
        )
        self._created.append(created)

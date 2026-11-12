"""The Tier List action's menu: Send to tier, Clear tier, Set series tier, Read State, and Settings."""

from collections.abc import Iterable
from functools import partial
from typing import Any

from qt.core import QMenu

from ..tiers import Tier
from .adapters import tier_list
from .icons import tier_swatch
from .series_menu import add_items as add_series_items


class TierMenu:
    """Builds and rebuilds the action's menu over the current library."""

    def __init__(self, action: Any) -> None:
        self._action = action
        self._created: list[Any] = []
        self._unregistered: list[Any] = []
        self._menu = QMenu()
        self._submenu = self._menu.addMenu(_('Send to tier'))
        self._series_submenu = self._menu.addMenu(_('Set series tier'))
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
        self._series_submenu.clear()
        if db is None:
            db = self._action.gui.current_db
        app = tier_list(db)
        if app.tier_column_ready():
            self._add_tiers(app.tier_config().tiers)
        else:
            self._add_missing(db)
        # Overrides live in prefs, so this submenu does not need the tier column.
        add_series_items(self._series_submenu, app.tier_config().tiers, self._action, self._register)
        self._add_read_state(app, db)
        self._add_settings()
        keyboard.finalize()

    def _add_tiers(self, tiers: Iterable[Tier]) -> None:
        for tier in tiers:
            self._register(
                self._submenu,
                f'send-to-tier-{tier.id}',
                tier.label,
                _('Send to tier: {}').format(tier.label),
                partial(self._send, tier.id),
                icon=tier_swatch(tier.colour),
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

    def _add_settings(self) -> None:
        """An Arrange board… item and a Settings… item at the bottom: the dialog over this library's config."""
        self._unregistered.append(self._menu.addSeparator())
        self._unregistered.append(self._menu.addAction(_('Arrange board…'), self._action.open_arrange))
        self._unregistered.append(self._menu.addAction(_('Settings…'), self._action.open_settings))

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

    def _register(
        self, menu: Any, unique_name: str, text: str, shortcut_name: str, triggered: Any, icon: Any = None
    ) -> None:
        created = self._action.create_menu_action(
            menu,
            unique_name,
            text,
            icon=icon,
            shortcut=None,
            shortcut_name=shortcut_name,
            triggered=triggered,
            persist_shortcut=True,
        )
        self._created.append(created)

"""A stand-in for calibre's main window, and loading the Tier List action into it."""

import importlib
from typing import Any

from calibre.customize.ui import find_plugin
from calibre.gui2.keyboard import Manager
from qt.core import QMainWindow


class FakeModel:
    def __init__(self, db: Any) -> None:
        self.db = db
        self.refreshed: list[list[int]] = []

    def refresh_ids(self, ids: list[int]) -> None:
        self.refreshed.append(list(ids))


class FakeLibraryView:
    def __init__(self, db: Any, ids: list[int]) -> None:
        self._ids = ids
        self._model = FakeModel(db)

    def get_selected_ids(self) -> list[int]:
        return list(self._ids)

    def model(self) -> FakeModel:
        return self._model


class FakeGui(QMainWindow):
    def __init__(self, db: Any, ids: list[int]) -> None:
        super().__init__()
        self.keyboard = Manager(self)
        self.current_db = db
        self.iactions: dict[str, Any] = {}
        self.library_view = FakeLibraryView(db, ids)


def load_action(gui: Any) -> Any:
    """A fresh Tier List action on this gui, through genesis and initialization."""
    plugin = find_plugin('Tier List')
    if plugin is None or plugin.actual_plugin is None:
        raise SystemExit('FAIL: the Tier List plugin is not registered')
    # load_actual_plugin caches one action per plugin; each check needs its own gui.
    module_name, class_name = plugin.actual_plugin.split(':')
    action = getattr(importlib.import_module(module_name), class_name)(gui, plugin.site_customization)
    action.interface_action_base_plugin = plugin
    action.do_genesis()
    action.initialization_complete()
    return action


def menu_shortcuts(gui: Any, action: Any) -> dict[str, dict[str, Any]]:
    """The keyboard shortcuts registered for the action's menu items."""
    prefix = f'{action.unique_name} : menu action : '
    return {name: shortcut for name, shortcut in gui.keyboard.shortcuts.items() if name.startswith(prefix)}

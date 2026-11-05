"""Integration smoke test for the installed zip.

Run with ``calibre-debug -e plugin/itest/smoke.py`` after installing
``dist/tierlist.zip`` with ``calibre-customize -a`` into a throwaway
``CALIBRE_CONFIG_DIRECTORY``. Prints ``SMOKE OK`` and exits 0 on success.

calibre runs Python with -OO, which strips ``assert``; use ``expect``.
"""

import importlib
import sys
from types import SimpleNamespace
from typing import Any

from calibre.customize.ui import find_plugin
from calibre.gui2 import gprefs
from calibre.gui2.actions import InterfaceAction

NAME = 'Tier List'
TOOLBAR = 'action-layout-toolbar'
CONTEXT_MENU = 'action-layout-context-menu'
LAYOUT_KEYS = (TOOLBAR, CONTEXT_MENU)


def expect(ok: bool, message: object) -> None:
    if not ok:
        raise SystemExit(f'SMOKE FAIL: {message}')


def check() -> None:
    plugin = find_plugin(NAME)
    if plugin is None or plugin.actual_plugin is None:
        raise SystemExit('SMOKE FAIL: the Tier List plugin is not registered')
    expect(plugin.version == (0, 1, 0), f'unexpected version: {plugin.version}')
    expect(plugin.minimum_calibre_version == (9, 0, 0), f'unexpected minimum: {plugin.minimum_calibre_version}')
    module_name, class_name = plugin.actual_plugin.split(':')
    action_class = getattr(importlib.import_module(module_name), class_name)
    expect(issubclass(action_class, InterfaceAction), action_class)
    expect(action_class.name == NAME, action_class.name)
    check_layout_claim(action_class)


def check_layout_claim(action_class: Any) -> None:
    """First load places the action on the toolbar and context menu; a later
    load must not undo the user removing it."""
    action = SimpleNamespace(name=NAME)
    action_class.add_to_action_layouts(action)
    action_class.add_to_action_layouts(action)
    for key in LAYOUT_KEYS:
        expect(list(gprefs[key]).count(NAME) == 1, (key, gprefs[key]))
    gprefs[CONTEXT_MENU] = tuple(x for x in gprefs[CONTEXT_MENU] if x != NAME)
    action_class.add_to_action_layouts(action)
    expect(NAME not in gprefs[CONTEXT_MENU], 're-added to the context menu after the user removed it')


def main() -> int:
    check()
    print('SMOKE OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())

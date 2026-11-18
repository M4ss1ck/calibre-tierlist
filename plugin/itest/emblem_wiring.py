"""Integration test for emblem wiring: opening a library syncs its emblems and resets the view once.

Run with ``calibre-debug -e plugin/itest/emblem_wiring.py`` after installing the zip into a throwaway
``CALIBRE_CONFIG_DIRECTORY``. Prints ``EMBLEM WIRING OK``; use ``expect``, as calibre runs Python with -OO.
"""

import sys
import tempfile

from calibre.gui2 import Application
from calibre_plugins.tierlist.calibre_ui.emblem_sync import RULE_PREFS
from calibre_plugins.tierlist.emblems import is_ours
from emblems import expect, open_library, rules, with_emblems
from fake_gui import FakeGui, load_action


def check_wiring(path: str) -> None:
    """Toggling emblems on in a loaded library writes the rules, and resets the model once."""
    db = open_library(path)
    try:
        gui = FakeGui(db, [])
        action = load_action(gui)
        expect(gui.library_view.model().resets == 0, 'loading the action reset the model')
        with_emblems(db, True)
        action.library_changed(db)
        for pref in RULE_PREFS:
            expect(len([rule for rule in rules(db, pref) if is_ours(rule)]) == 1, f'{pref} after library_changed')
        resets = gui.library_view.model().resets
        expect(resets == 1, f'library_changed reset the model {resets} times')
    finally:
        db.close()


def main() -> int:
    Application([])
    with tempfile.TemporaryDirectory() as tmp:
        check_wiring(tmp + '/wiring')
    print('EMBLEM WIRING OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())

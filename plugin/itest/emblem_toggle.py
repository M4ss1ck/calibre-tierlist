"""Integration test for the Settings emblem toggle: the checkbox, its note, and calibre's consent prompt.

Run with ``calibre-debug -e plugin/itest/emblem_toggle.py`` after installing the zip into a throwaway
``CALIBRE_CONFIG_DIRECTORY``. Prints ``EMBLEM TOGGLE OK``; use ``expect``, as calibre runs Python with -OO.
The prompt is stubbed: offscreen Qt cannot click a modal dialog.
"""

import sys
import tempfile
from dataclasses import replace
from typing import Any, ClassVar

from calibre.gui2 import Application, gprefs
from calibre_plugins.tierlist.calibre_ui import emblem_toggle as toggle_module
from calibre_plugins.tierlist.calibre_ui.adapters import config_admin
from calibre_plugins.tierlist.calibre_ui.config_tiers import TiersTab
from calibre_plugins.tierlist.calibre_ui.emblem_toggle import EmblemToggle, emblems_hidden, show_emblems
from settings import open_library

ASKED: list[Any] = []
ANSWER: list[bool] = [True]


def expect(ok: bool, message: object) -> None:
    if not ok:
        raise SystemExit(f'EMBLEM TOGGLE FAIL: {message}')


def ask(*args: Any) -> bool:
    """Stand in for question_dialog: record the ask, and answer as the current check wants."""
    ASKED.append(args)
    return ANSWER[0]


def tick(toggle: EmblemToggle, answer: bool = True) -> None:
    """Tick the checkbox as a user would, with the prompt set to refuse when ``answer`` is False."""
    ANSWER[0] = answer
    ASKED.clear()
    toggle.checkbox.click()


def check_toggle() -> None:
    """A tick asks once while calibre hides emblems: yes turns them on, no notes it; nothing else asks."""
    gprefs['emblem_style'] = 'none'
    yes = EmblemToggle()
    tick(yes)
    expect(gprefs['emblem_style'] == 'emboss', f'yes stored {gprefs["emblem_style"]!r}')
    expect(len(ASKED) == 1, f'{len(ASKED)} prompts on the first tick')
    expect(yes.checked() and yes.note.isHidden(), 'the note shows although emblems are on')
    gprefs['emblem_style'] = 'none'
    no = EmblemToggle()
    tick(no, False)
    expect(gprefs['emblem_style'] == 'none', f'no stored {gprefs["emblem_style"]!r}')
    expect(len(ASKED) == 1, f'{len(ASKED)} prompts on a refused tick')
    expect(not no.note.isHidden(), 'the note is hidden although calibre hides the emblems')
    gprefs['emblem_style'] = 'emboss'
    already = EmblemToggle()
    tick(already, False)
    expect(already.checked() and not ASKED, f'{len(ASKED)} prompts with emblems already on')
    gprefs['emblem_style'] = 'none'
    stored = EmblemToggle()
    stored.set_checked(True)
    expect(stored.checked() and not ASKED, f'{len(ASKED)} prompts on set_checked')
    tick(stored, False)
    expect(not stored.checked() and not ASKED, f'{len(ASKED)} prompts on unticking')

    class LegacyPrefs(dict[str, Any]):
        """A calibre 9.0 to 9.3 gprefs: show_emblems, and no emblem_style among its defaults."""

        defaults: ClassVar[dict[str, Any]] = {}

    prefs = LegacyPrefs()
    expect(emblems_hidden(prefs), 'a missing show_emblems is not hidden')
    prefs['show_emblems'] = False
    expect(emblems_hidden(prefs), 'show_emblems False is not hidden')
    prefs['show_emblems'] = True
    expect(not emblems_hidden(prefs), 'show_emblems True is hidden')
    show_emblems(prefs)
    expect(prefs.get('show_emblems') is True and 'emblem_style' not in prefs, f'legacy wrote {prefs}')


def check_tiers_tab(path: str) -> None:
    """The Tiers tab's checkbox is what build_config stores, and load_tiers carries a stored choice."""
    db = open_library(path)
    try:
        tab = TiersTab(config_admin(db))
        expect(not tab.build_config().emblems, 'emblems start on')
        tab.emblems.set_checked(True)
        expect(tab.build_config().emblems, 'build_config ignored the checkbox')
        chosen = tab.build_config()
        tab.emblems.set_checked(False)
        tab.load_tiers(replace(chosen, emblems=True))
        expect(tab.build_config().emblems, 'load_tiers ignored emblems')
    finally:
        db.close()


def main() -> int:
    Application([])
    expect('emblem_style' in gprefs.defaults, 'this calibre has no emblem_style pref, so it predates 9.4')
    original = gprefs.get('emblem_style')
    toggle_module.question_dialog = ask
    try:
        check_toggle()
        with tempfile.TemporaryDirectory() as tmp:
            check_tiers_tab(tmp + '/tiers')
    finally:
        gprefs['emblem_style'] = 'none' if original is None else original
    print('EMBLEM TOGGLE OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())

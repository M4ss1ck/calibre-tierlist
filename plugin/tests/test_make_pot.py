"""The translation template: calibre's `_` and `ngettext` calls, one .pot file.

Runs the real xgettext over the real source tree; any machine without GNU
gettext skips instead of failing.
"""

import shutil
from pathlib import Path

import make_pot
import pytest

pytestmark = pytest.mark.skipif(shutil.which('xgettext') is None, reason='xgettext is not installed')


def test_pot_holds_the_plugins_strings(tmp_path: Path) -> None:
    pot = make_pot.build_pot(tmp_path / 'tierlist.pot').read_text(encoding='utf-8')

    assert 'msgid "Compiling tier list"' in pot
    assert 'msgid_plural' in pot
    assert '#: plugin/src/tierlist/' in pot
    assert 'Tier List' in pot.split('Project-Id-Version:')[1].split('\n')[0]

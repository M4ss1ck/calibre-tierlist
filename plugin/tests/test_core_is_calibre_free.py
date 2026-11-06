"""The core must import nothing from calibre or Qt (checked in a clean interpreter)."""

import os
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / 'src'

CODE = """
import importlib, pkgutil, sys
import tierlist

for info in pkgutil.walk_packages(tierlist.__path__, 'tierlist.'):
    if info.name == 'tierlist.calibre_ui' or info.name.startswith('tierlist.calibre_ui.'):
        continue
    importlib.import_module(info.name)

offenders = sorted({m.split('.')[0] for m in sys.modules} & {'calibre', 'qt'})
assert not offenders, offenders
"""


def test_core_imports_pull_in_no_calibre_or_qt() -> None:
    env = dict(os.environ, PYTHONPATH=str(SRC))
    result = subprocess.run([sys.executable, '-c', CODE], env=env, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr

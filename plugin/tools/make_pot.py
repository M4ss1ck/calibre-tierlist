"""Regenerate plugin/translations/tierlist.pot: every string a translator sees.

Standard library only; needs GNU xgettext on PATH.
"""

from __future__ import annotations

import shutil
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'plugin' / 'src' / 'tierlist'
ENTRY = ROOT / 'plugin' / 'calibre_entry.py'
PYPROJECT = ROOT / 'plugin' / 'pyproject.toml'
OUT = ROOT / 'plugin' / 'translations' / 'tierlist.pot'
SKIP_DIRS = {'__pycache__'}


def sources() -> list[Path]:
    """Every Python file holding translatable strings, in a stable order."""
    found = [path for path in sorted(SRC.rglob('*.py')) if not SKIP_DIRS & set(path.relative_to(SRC).parts)]
    return [*found, ENTRY]


def version() -> str:
    return tomllib.loads(PYPROJECT.read_text(encoding='utf-8'))['project']['version']


def build_pot(out: Path = OUT) -> Path:
    """Write the translation template for the plugin's strings to `out`."""
    xgettext = shutil.which('xgettext')
    if xgettext is None:
        raise SystemExit('xgettext not found: install GNU gettext (gettext-tools)')
    out.parent.mkdir(parents=True, exist_ok=True)
    # Paths stay relative to the repo root, so the #: references are stable.
    subprocess.run(
        [
            xgettext,
            '--language=Python',
            '--from-code=UTF-8',
            '--keyword=_',
            '--keyword=ngettext:1,2',
            '--add-comments',
            '--sort-by-file',
            '--package-name=Tier List',
            f'--package-version={version()}',
            f'--output={out}',
            *(path.relative_to(ROOT).as_posix() for path in sources()),
        ],
        cwd=ROOT,
        check=True,
    )
    return out


def main() -> None:
    print(f'wrote {build_pot()}')


if __name__ == '__main__':
    main()

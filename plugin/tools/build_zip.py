"""Build dist/tierlist.zip: the plugin package plus its zip-root entry point.

Standard library only; `web/dist/template.html` is included when the web
package has been built, and skipped otherwise.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'plugin' / 'src' / 'tierlist'
ENTRY = ROOT / 'plugin' / 'calibre_entry.py'
TEMPLATE = ROOT / 'web' / 'dist' / 'template.html'
OUT = ROOT / 'dist' / 'tierlist.zip'
SKIP_DIRS = {'__pycache__'}


def payload() -> list[tuple[str, bytes]]:
    """(archive name, content) pairs for the zip, in a stable order."""
    files: list[tuple[str, bytes]] = []
    for path in sorted(SRC.rglob('*')):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.relative_to(SRC).parts):
            continue
        name = path.relative_to(SRC).as_posix()
        files.append((name, ENTRY.read_bytes() if name == '__init__.py' else path.read_bytes()))
    files.append(('plugin-import-name-tierlist.txt', b''))
    if TEMPLATE.is_file():
        files.append(('template.html', TEMPLATE.read_bytes()))
    return files


def build(out: Path = OUT) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zf:
        for name, data in payload():
            zf.writestr(name, data)
    return out


def main() -> None:
    print(f'wrote {build()}')


if __name__ == '__main__':
    main()

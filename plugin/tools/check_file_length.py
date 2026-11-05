"""File length gate: WARN past the soft cap, ERROR past the hard cap.

Walks the given roots for *.py, *.ts and *.svelte files, skipping vendored and
generated trees. Exits 1 when any file is over the hard cap.
"""

from __future__ import annotations

import sys
from collections.abc import Iterable, Iterator
from pathlib import Path

SOFT = 100
HARD = 150
SUFFIXES = {'.py', '.ts', '.svelte'}
SKIP_DIRS = {'node_modules', '.venv', 'dist', '__pycache__', 'typings', '.git'}
SKIP_NAMES = ('.d.ts',)


def source_files(roots: Iterable[str]) -> Iterator[Path]:
    for given in roots:
        root = Path(given)
        if root.is_file():
            yield root
            continue
        for path in sorted(root.rglob('*')):
            relative = path.relative_to(root)
            if not path.is_file() or path.suffix not in SUFFIXES:
                continue
            if any(part in SKIP_DIRS for part in relative.parts):
                continue
            if path.name.endswith(SKIP_NAMES):
                continue
            yield path


def main(argv: list[str] | None = None) -> int:
    roots = sys.argv[1:] if argv is None else argv
    failures = 0
    for path in source_files(roots):
        lines = len(path.read_text(encoding='utf-8').splitlines())
        if lines > HARD:
            print(f'ERROR {path}: {lines} lines (hard cap {HARD})')
            failures += 1
        elif lines > SOFT:
            print(f'WARN {path}: {lines} lines (soft cap {SOFT})')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())

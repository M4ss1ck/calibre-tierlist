"""Performance budget: a generated 1,000-book library compiles in under ten seconds.

Run with ``calibre-debug -e plugin/itest/perf.py`` after installing ``dist/tierlist.zip``
with ``calibre-customize -a`` into a throwaway ``CALIBRE_CONFIG_DIRECTORY``. Builds the
fixture in a temp dir, compiles it through the same entry ``compile.py`` uses, and reads
the seconds and byte size off the stats line the compile logs. Prints ``PERF <books>
books in <seconds>s, <bytes> bytes`` then ``PERF OK``; exits non-zero on ``PERF FAIL``.
``PERF_REPORT_ONLY=1`` reports an over-budget time without failing: calibre builds before
9.18 bundle a non-SIMD libwebp about ten times slower, so CI enforces on latest only.

calibre runs Python with -OO, which strips ``assert``; use ``expect``.
"""

import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

from calibre.gui2 import Application
from calibre_plugins.tierlist.calibre_ui.adapters import tier_list
from calibre_plugins.tierlist.calibre_ui.compile_job import run_compile
from calibre_plugins.tierlist.compile import CompileRequest
from fixture_library import BOOKS, build

BUDGET_SECONDS = 10.0
# The fixture is seeded, so these are fixed: they keep the budget honest, since a compile that
# quietly drops books would finish faster and still pass.
EXPECTED_ON_BOARD = 954
EXPECTED_SERIES = 113
REPO = Path(__file__).resolve().parents[2]
TEMPLATE = REPO / 'web' / 'dist' / 'template.html'
STATS = re.compile(
    r'Tier List compiled: (\d+) of (\d+) books, (\d+) series, (\d+) covers as \w+ in ([\d.]+)s, (\d+) bytes'
)


def expect(ok: bool, message: object) -> None:
    if not ok:
        raise SystemExit(f'PERF FAIL: {message}')


def measure(db: Any, path: str) -> tuple[float, int]:
    """Compile every book in this library and return the seconds and byte size its stats line reports."""
    request = CompileRequest('library', tuple(sorted(db.new_api.all_book_ids())), 'Perf', '0.1.0')
    lines: list[str] = []
    run_compile(tier_list(db), request, TEMPLATE.read_text(encoding='utf-8'), path, lines.append)
    expect(len(lines) == 1, lines)
    match = STATS.search(lines[0])
    if match is None:
        raise SystemExit(f'PERF FAIL: no stats line in {lines[0]}')
    on_board, scope, series_count, cover_count, seconds, size = match.groups()
    expect(int(on_board) == EXPECTED_ON_BOARD, f'{on_board} books on the board, expected {EXPECTED_ON_BOARD}')
    expect(int(scope) == BOOKS, f'the compile covered {scope} books instead of {BOOKS}')
    expect(int(series_count) == EXPECTED_SERIES, f'{series_count} series, expected {EXPECTED_SERIES}')
    expect(int(cover_count) == EXPECTED_ON_BOARD, f'{cover_count} covers, expected one per book on the board')
    return float(seconds), int(size)


def main() -> int:
    expect(TEMPLATE.is_file(), f'no template at {TEMPLATE}; run just build first')
    Application([])
    with tempfile.TemporaryDirectory() as tmp:
        db = build(tmp + '/perf-library')
        try:
            seconds, size = measure(db, tmp + '/perf.html')
        finally:
            db.close()
    print(f'PERF {BOOKS} books in {seconds:.2f}s, {size} bytes')
    if seconds >= BUDGET_SECONDS:
        if os.environ.get('PERF_REPORT_ONLY') == '1':
            print(f'PERF OVER BUDGET (report only): {seconds:.2f}s')
            return 0
        print(f'PERF FAIL: {seconds:.2f}s is over the {BUDGET_SECONDS:.0f}s budget')
        return 1
    print('PERF OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())

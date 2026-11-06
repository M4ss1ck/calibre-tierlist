"""Integration test for cover thumbnails: the formats on offer, the encoding, and the compiled data URI.

Run with ``calibre-debug -e plugin/itest/covers.py`` after installing
``dist/tierlist.zip`` with ``calibre-customize -a`` into a throwaway
``CALIBRE_CONFIG_DIRECTORY``. Prints ``COVERS OK`` and exits 0 on success.

calibre runs Python with -OO, which strips ``assert``; use ``expect``.
"""

import sys
import tempfile
from pathlib import Path
from typing import Any

from calibre.ebooks.metadata.book.base import Metadata
from calibre.gui2 import Application
from calibre.library import db as open_db
from calibre.utils.img import image_from_data, image_to_data
from calibre_plugins.tierlist.app import TierList
from calibre_plugins.tierlist.calibre_ui import covers as covers_module
from calibre_plugins.tierlist.calibre_ui.adapters import tier_list
from calibre_plugins.tierlist.calibre_ui.compile_job import run_compile
from calibre_plugins.tierlist.calibre_ui.covers import CalibreCovers
from calibre_plugins.tierlist.compile import COVER_WIDTH, CompileRequest, choose_format
from qt.core import QColor, QImage, QImageWriter

TITLES = ('With Cover', 'Without Cover')
RED = (255, 0, 0)
# calibre stores covers as JPEG, so a solid fill comes back a shade or two off the exact colour.
TOLERANCE = 8
REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / 'dist' / 'itest' / 'covers.html'
TEMPLATE = REPO / 'web' / 'dist' / 'template.html'


def expect(ok: bool, message: object) -> None:
    if not ok:
        raise SystemExit(f'COVERS FAIL: {message}')


def red_png() -> bytes:
    img = QImage(600, 900, QImage.Format.Format_RGB32)
    img.fill(QColor('#ff0000'))
    return image_to_data(img, fmt='PNG')


def library(path: str) -> Any:
    db = open_db(path)
    db.create_custom_column('tier', 'Tier', 'text', False)
    db.create_custom_column('date_read', 'Date read', 'datetime', False)
    db.close()
    return open_db(path)


def covered_library(path: str) -> tuple[Any, int, int, TierList]:
    """A library of two tiered books, only the first of which has a cover."""
    db = library(path)
    covered = db.new_api.create_book_entry(Metadata(TITLES[0], ['Author']))
    bare = db.new_api.create_book_entry(Metadata(TITLES[1], ['Author']))
    db.new_api.set_cover({covered: red_png()})
    app: TierList = tier_list(db)
    app.set_book_tier([covered, bare], 'a')
    return db, covered, bare, app


def qt_writable() -> frozenset[str]:
    """The formats this Qt can both encode and decode, lowercased."""
    return frozenset(bytes(name).decode('ascii').lower() for name in QImageWriter.supportedImageFormats())


def is_red(colour: str) -> bool:
    """True when a '#rrggbb' colour is the solid red fill, up to calibre's JPEG cover storage."""
    if len(colour) != 7 or not colour.startswith('#'):
        return False
    try:
        channels = [int(colour[start : start + 2], 16) for start in (1, 3, 5)]
    except ValueError:
        return False
    return all(abs(got - want) <= TOLERANCE for got, want in zip(channels, RED, strict=True))


def check_thumbnail(covers: CalibreCovers, book_id: int, fmt: str, writable: frozenset[str]) -> None:
    cover = covers.cover(book_id, fmt, COVER_WIDTH)
    if cover is None:
        raise SystemExit(f'COVERS FAIL: a book with a cover produced no {fmt} thumbnail')
    expect(cover.format == fmt, cover.format)
    expect(len(cover.data) > 0, f'empty {fmt} bytes')
    expect(is_red(cover.colour), f'the {fmt} dominant colour was {cover.colour}')
    if fmt in writable:
        image = image_from_data(cover.data)
        expect(image.width() == COVER_WIDTH, f'the {fmt} thumbnail was {image.width()} px wide')


def check_compile(app: TierList, book_ids: tuple[int, ...], fmt: str) -> None:
    request = CompileRequest('library', tuple(sorted(book_ids)), 'Covers', '0.1.0')
    lines: list[str] = []
    written = run_compile(app, request, TEMPLATE.read_text(encoding='utf-8'), str(OUTPUT), lines.append)
    expect(written == str(OUTPUT), written)
    expect(OUTPUT.is_file(), f'no compiled file at {OUTPUT}')
    expect(len(lines) == 1 and f'1 covers as {fmt}' in lines[0], lines)
    html = OUTPUT.read_text(encoding='utf-8')
    expect(f'data:image/{fmt};base64,' in html, f'no {fmt} data URI in the compiled HTML')


def check_probe(db: Any) -> None:
    """A format whose every encoder fails is not offered, even when Qt lists it (AVIF without an encoder)."""
    real = covers_module.ENCODERS

    def failing(encode: covers_module.Encoder) -> covers_module.Encoder:
        def wrapped(img: Any, fmt: str) -> bytes:
            if fmt == 'webp':
                raise RuntimeError('Failed to encode image: No codec available')
            return encode(img, fmt)

        return wrapped

    covers_module.ENCODERS = tuple(failing(encode) for encode in real)
    try:
        offered = CalibreCovers(db).formats()
    finally:
        covers_module.ENCODERS = real
    expect('webp' not in offered and 'jpeg' in offered, f'a failing encoder was offered: {sorted(offered)}')


def main() -> int:
    Application([])
    with tempfile.TemporaryDirectory() as tmp:
        db, covered, bare, app = covered_library(tmp + '/covers')
        try:
            covers = CalibreCovers(db)
            available = covers.formats()
            fmt = choose_format(available)
            print(f'formats: {sorted(available)}, chosen: {fmt}')
            writable = qt_writable()
            for one in sorted(available):
                check_thumbnail(covers, covered, one, writable)
            expect(covers.cover(bare, fmt, COVER_WIDTH) is None, 'a book without a cover produced a thumbnail')
            check_compile(app, (covered, bare), fmt)
            check_probe(db)
        finally:
            db.close()
    print(f'COVERS OK {fmt}')
    return 0


if __name__ == '__main__':
    sys.exit(main())

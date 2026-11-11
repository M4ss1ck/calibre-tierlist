"""A reproducible 1,000-book calibre library, for the performance budget itest.

Run with ``calibre-debug -e plugin/itest/fixture_library.py <dir>`` to build one, or import
``build(path)``. A fixed seed and fixed dates make two builds hold the same books, Book
Tiers, Read States, and covers.
"""

import random
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from calibre.ebooks.metadata.book.base import Metadata
from calibre.gui2 import Application
from calibre.library import db as open_db
from calibre.utils.img import image_to_data
from calibre_plugins.tierlist.calibre_ui.adapters import CalibreLibrary, tier_list
from calibre_plugins.tierlist.tiers import DEFAULT_TIER_CONFIG
from qt.core import QColor, QImage, QPainter

BOOKS, SEED, SERIES_TARGET = 1000, 14, 600
TIERS = tuple(tier.id for tier in DEFAULT_TIER_CONFIG.tiers)
TAGS = ('fantasy', 'history', 'mystery', 'poetry', 'science', 'travel')
COVER_SIZE = (600, 900)


@dataclass(frozen=True)
class Planned:
    """One book to create: its title and series, and the Book Tier and Read State to give it."""

    title: str
    series: str | None
    index: int
    tier: str | None
    date_read: date | None


def make_plan(rng: random.Random) -> list[Planned]:
    """The books to create: series of three to eight members, then standalones, up to 1,000."""
    plan: list[Planned] = []
    series_no = 0
    while len(plan) < SERIES_TARGET:
        series_no += 1
        name = f'Series {series_no}'
        for index in range(1, rng.randint(3, 8) + 1):
            plan.append(planned(rng, len(plan), name, index))
    while len(plan) < BOOKS:
        plan.append(planned(rng, len(plan), None, 0))
    return plan[:BOOKS]


def planned(rng: random.Random, number: int, series: str | None, index: int) -> Planned:
    """One planned book: most are tiered, most are read, and most reads carry a fixed date."""
    tier = rng.choice(TIERS) if rng.random() < 0.85 else None
    read = tier is not None or rng.random() < 0.5
    title = f'{series} #{index}' if series is not None else f'Standalone {number + 1}'
    dated = read and rng.random() < 0.8
    return Planned(
        title, series, index, tier, date(2020, 1, 1) + timedelta(days=rng.randrange(6 * 365)) if dated else None
    )


def metadata(book: Planned, number: int) -> Metadata:
    """The calibre metadata for one planned book; authors, rating and tags step with its number."""
    mi = Metadata(book.title, [f'Author {number % 40 + 1}'])
    mi.series, mi.series_index = book.series, float(book.index) if book.series else None
    mi.rating, mi.tags = (0, 0, 6, 8, 10)[number % 5], [TAGS[number % len(TAGS)]]
    mi.comments = f'<p>{book.title} is a fixture book. <i>Nothing here is real.</i></p>'
    return mi


def cover(number: int) -> bytes:
    """A generated 600x900 cover like a real one: a spine band and a title block over a fill, as JPEG bytes."""
    width, height = COVER_SIZE

    def tone(step: int) -> QColor:
        steps = number + step
        return QColor(f'#{64 + steps * 37 % 160:02x}{64 + steps * 71 % 160:02x}{64 + steps * 113 % 160:02x}')

    img = QImage(width, height, QImage.Format.Format_RGB32)
    painter = QPainter(img)
    painter.fillRect(0, 0, width, height, tone(0))
    painter.fillRect(0, 0, width, 120, tone(90))
    painter.fillRect(60, 300, width - 120, 260, tone(180))
    painter.end()
    return image_to_data(img, compression_quality=85, fmt='JPEG')


def build(path: str) -> Any:
    """Create the 1,000-book library at `path` and return it open, with fixed dates for every book."""
    db = open_db(path)
    db.create_custom_column('tier', 'Tier', 'text', False)
    db.create_custom_column('date_read', 'Date read', 'datetime', False)
    db.close()
    db = open_db(path)
    # calibre commits a dozen transactions per created book; skipping the fsync on this throwaway
    # temp library turns 1,000 entries from half a minute into a few seconds.
    db.new_api.backend.conn.execute('PRAGMA synchronous=OFF')
    db.new_api.backend.conn.execute('PRAGMA journal_mode=MEMORY')
    plan = make_plan(random.Random(SEED))
    ids = [db.new_api.create_book_entry(metadata(book, number)) for number, book in enumerate(plan)]
    app = tier_list(db)
    for tier in TIERS:
        # One write per Tier, through the plugin's own use case, as the compile itest does.
        chosen = [book_id for book_id, book in zip(ids, plan, strict=True) if book.tier == tier]
        if chosen:
            app.set_book_tier(chosen, tier)
    # set_book_tier marks every tiered book read with today's date; write the planned dates instead,
    # so the fixture carries no wall-clock data.
    CalibreLibrary(db).write_field(
        '#date_read', {book_id: book.date_read for book_id, book in zip(ids, plan, strict=True)}
    )
    db.new_api.set_cover({book_id: cover(number) for number, book_id in enumerate(ids)})
    return db


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('usage: calibre-debug -e plugin/itest/fixture_library.py <library dir>')
    Application([])
    library = build(sys.argv[1])
    try:
        print(f'FIXTURE OK {len(library.new_api.all_book_ids())} books at {library.library_path}')
    finally:
        library.close()

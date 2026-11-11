"""A reproducible 1,000-book calibre library, for the performance budget itest.

Run with ``calibre-debug -e plugin/itest/fixture_library.py <dir>`` to build one, or
import ``build(path)`` from another itest script. A fixed seed and fixed dates make
two builds hold the same books, Book Tiers, Read States, and covers.
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
from qt.core import QColor, QImage

BOOKS = 1000
SEED = 14
SERIES_TARGET = 600
TIERS = ('s', 'a', 'b', 'c', 'd', 'f')
TAGS = ('fantasy', 'history', 'mystery', 'poetry', 'science', 'travel')
COVER_SIZE = (60, 90)
FIRST_DAY = date(2020, 1, 1)
DAY_SPAN = 6 * 365


@dataclass(frozen=True)
class Planned:
    """One book to create: what calibre stores, and the Book Tier and Read State to give it."""

    title: str
    authors: tuple[str, ...]
    series: str | None
    index: int
    tier: str | None
    date_read: date | None
    rating: int
    tags: tuple[str, ...]
    comments: str


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
    return Planned(
        title,
        (f'Author {rng.randint(1, 40)}',),
        series,
        index,
        tier,
        FIRST_DAY + timedelta(days=rng.randrange(DAY_SPAN)) if read and rng.random() < 0.8 else None,
        rng.choice((0, 0, 6, 8, 10)),
        tuple(rng.sample(TAGS, rng.randint(0, 2))),
        f'<p>{title} is the {rng.randint(1, 9)}th book an agent read for this fixture. '
        f'<i>Nothing here is real.</i></p>',
    )


def metadata(book: Planned) -> Metadata:
    """The calibre metadata for one planned book."""
    mi = Metadata(book.title, list(book.authors))
    mi.series = book.series
    mi.series_index = float(book.index) if book.series else None
    mi.rating, mi.tags, mi.comments = book.rating, list(book.tags), book.comments
    return mi


def cover(number: int) -> bytes:
    """A small generated cover: a solid fill in this book's own colour, as PNG bytes."""
    img = QImage(*COVER_SIZE, QImage.Format.Format_RGB32)
    # Mid-tone colours a fixed stride apart, so neighbouring covers are easy to tell apart.
    img.fill(QColor(f'#{64 + number * 37 % 160:02x}{64 + number * 71 % 160:02x}{64 + number * 113 % 160:02x}'))
    return image_to_data(img, fmt='PNG')


def build(path: str) -> Any:
    """Create the 1,000-book library at `path` and return it open, with fixed dates for every book."""
    db = open_db(path)
    db.create_custom_column('tier', 'Tier', 'text', False)
    db.create_custom_column('date_read', 'Date read', 'datetime', False)
    db.close()
    db = open_db(path)
    # calibre commits a dozen transactions per created book; skipping the fsync on this throwaway
    # temp library turns 1,000 entries from half a minute into under a second.
    db.new_api.backend.conn.execute('PRAGMA synchronous=OFF')
    db.new_api.backend.conn.execute('PRAGMA journal_mode=MEMORY')
    plan = make_plan(random.Random(SEED))
    ids = [db.new_api.create_book_entry(metadata(book)) for book in plan]
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


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print('usage: calibre-debug -e plugin/itest/fixture_library.py <library dir>')
        return 2
    Application([])
    db = build(argv[1])
    try:
        print(f'FIXTURE OK {len(db.new_api.all_book_ids())} books at {db.library_path}')
    finally:
        db.close()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

"""Build Tier List Data from the books the library holds."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime

from ..ports import Library
from ..tiers import Tier, TierConfig
from .data import Book, Generated, Lane, TierListData

READ_COLUMN_TYPES = ('datetime', 'bool')


@dataclass(frozen=True)
class Row:
    """One book as read from the library, before compile filters and sorts it."""

    id: int
    title: str
    tier: object | None
    read: object | None


def compile_data(generated: Generated, library: Library, config: TierConfig, book_ids: Iterable[int]) -> TierListData:
    """Read these books from the library and build their Tier List Data."""
    ids = list(book_ids)
    titles = library.read_field('title', ids)
    tiers = library.read_field(config.tier_column, ids) if library.has_column(config.tier_column) else {}
    datatype = library.column_types().get(config.read_column)
    reads = library.read_field(config.read_column, ids) if datatype in READ_COLUMN_TYPES else {}
    rows = [Row(book_id, str(titles.get(book_id) or ''), tiers.get(book_id), reads.get(book_id)) for book_id in ids]
    return build(generated, config.tiers, rows, datatype == 'bool')


def build(generated: Generated, tiers: tuple[Tier, ...], rows: Iterable[Row], read_is_bool: bool) -> TierListData:
    """Keep read books, resolve their Book Tier, and place them in ordered Lanes."""
    known = {tier.id for tier in tiers}
    books: list[Book] = []
    for row in rows:
        raw_tier = row.tier if isinstance(row.tier, str) else None
        read = row.read is True if read_is_bool else row.read is not None
        if not (read or raw_tier):
            continue
        tier = raw_tier if raw_tier in known else None
        books.append(Book(row.id, row.title, tier, _date_read(row.read, read_is_bool)))
    ordered = tuple(sorted(books, key=lambda book: book.id))
    lanes = tuple(Lane(tier.id, _cards(books, tier.id)) for tier in tiers)
    return TierListData(generated, tiers, (*lanes, Lane(None, _cards(books, None))), ordered)


def _cards(books: list[Book], tier: str | None) -> tuple[int, ...]:
    matches = (book for book in books if book.tier == tier)
    return tuple(book.id for book in sorted(matches, key=_sort_key))


def _sort_key(book: Book) -> tuple[bool, date, str, int]:
    return (book.date_read is None, book.date_read or date.min, book.title.casefold(), book.id)


def _date_read(value: object, read_is_bool: bool) -> date | None:
    if read_is_bool or not isinstance(value, (date, datetime)):
        return None
    if isinstance(value, datetime):
        return value.astimezone().date() if value.tzinfo is not None else value.date()
    return value

"""Rows: one book as read from the library, and which rows belong on the board."""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from typing import cast

from .blurb import blurb
from .data import Book, Details
from .series import display_number


@dataclass(frozen=True)
class Row:
    id: int
    title: str
    tier: object | None
    read: object | None
    series: object | None = None
    index: object | None = None
    total: object | None = None
    authors: object | None = None
    rating: object | None = None
    tags: object | None = None
    comments: object | None = None


def on_board(rows: Iterable[Row], read_is_bool: bool, overridden: set[str]) -> list[Row]:
    """The rows whose books belong on the board: standalone qualifiers and every member of a series that qualifies or
    has an applicable Override."""
    rows = list(rows)
    appearing: set[str] = set()
    for row in rows:
        name = series_name(row)
        if name is not None and (name in overridden or _qualifies(row, read_is_bool)):
            appearing.add(name)
    board: list[Row] = []
    for row in rows:
        name = series_name(row)
        if name is not None:
            if name in appearing:
                board.append(row)
        elif _qualifies(row, read_is_bool):
            board.append(row)
    return board


def book_of(row: Row, known: set[str], read_is_bool: bool) -> Book:
    """Resolve one row into a Book on the board."""
    raw = _raw_tier(row)
    return Book(
        row.id,
        row.title,
        raw if raw in known else None,
        _date_read(row.read, read_is_bool),
        _is_read(row, read_is_bool),
        details_of(row),
    )


def details_of(row: Row) -> Details:
    """The detail panel fields of one row: calibre's 0-10 rating becomes 0.5-5 stars, 0 meaning unrated."""
    name = series_name(row)
    index = row.index if isinstance(row.index, (int, float)) and name is not None else None
    rating = row.rating if isinstance(row.rating, (int, float)) and row.rating > 0 else None
    return Details(
        _strings(row.authors),
        name,
        None if index is None else display_number(float(index)),
        None if rating is None else rating / 2,
        _strings(row.tags),
        blurb(row.comments),
    )


def _strings(value: object) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    items = cast(Sequence[object], value)
    return tuple(item for item in items if isinstance(item, str) and item)


def series_name(row: Row) -> str | None:
    """The row's non-empty series name, or None when it has none."""
    value = row.series
    return value if isinstance(value, str) and value else None


def _raw_tier(row: Row) -> str | None:
    return row.tier if isinstance(row.tier, str) and row.tier else None


def _qualifies(row: Row, read_is_bool: bool) -> bool:
    return _is_read(row, read_is_bool) or _raw_tier(row) is not None


def _is_read(row: Row, read_is_bool: bool) -> bool:
    return row.read is True if read_is_bool else row.read is not None


def _date_read(value: object, read_is_bool: bool) -> date | None:
    if read_is_bool or not isinstance(value, (date, datetime)):
        return None
    if isinstance(value, datetime):
        return value.astimezone().date() if value.tzinfo is not None else value.date()
    return value

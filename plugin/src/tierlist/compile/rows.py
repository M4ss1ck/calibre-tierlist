"""Rows: one book as read from the library, and which rows belong on the board."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime

from .data import Book


@dataclass(frozen=True)
class Row:
    id: int
    title: str
    tier: object | None
    read: object | None
    series: object | None = None
    index: object | None = None
    total: object | None = None


def on_board(rows: Iterable[Row], read_is_bool: bool) -> list[Row]:
    """The rows whose books belong on the board: standalone qualifiers and every member of an appearing series."""
    rows = list(rows)
    appearing: set[str] = set()
    for row in rows:
        name = series_name(row)
        if name is not None and _qualifies(row, read_is_bool):
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
    raw = row.tier if isinstance(row.tier, str) and row.tier else None
    return Book(
        row.id,
        row.title,
        raw if raw in known else None,
        _date_read(row.read, read_is_bool),
        _is_read(row, read_is_bool),
    )


def series_name(row: Row) -> str | None:
    """The row's non-empty series name, or None when it has none."""
    value = row.series
    return value if isinstance(value, str) and value else None


def _qualifies(row: Row, read_is_bool: bool) -> bool:
    return _is_read(row, read_is_bool) or (isinstance(row.tier, str) and bool(row.tier))


def _is_read(row: Row, read_is_bool: bool) -> bool:
    return row.read is True if read_is_bool else row.read is not None


def _date_read(value: object, read_is_bool: bool) -> date | None:
    if read_is_bool or not isinstance(value, (date, datetime)):
        return None
    if isinstance(value, datetime):
        return value.astimezone().date() if value.tzinfo is not None else value.date()
    return value

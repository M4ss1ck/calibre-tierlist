"""Read State: the column that holds it, mapping it, and marking books read and unread."""

from collections.abc import Iterable
from dataclasses import replace
from datetime import date

from .compile import READ_COLUMN_TYPES
from .ports import Library
from .tiers import TierConfig


def column_ready(library: Library, config: TierConfig) -> bool:
    """True when the column Tier Config names for Read State is a Date or Yes/No column."""
    return library.column_types().get(config.read_column) in READ_COLUMN_TYPES


def column_candidates(library: Library) -> list[str]:
    """The lookup names of every Date and Yes/No column in this library, sorted."""
    types = library.column_types()
    return sorted(lookup for lookup, datatype in types.items() if datatype in READ_COLUMN_TYPES)


def mapped(library: Library, config: TierConfig, lookup_name: str) -> TierConfig:
    """Tier Config pointing its Read State column at this Date or Yes/No column."""
    if lookup_name not in column_candidates(library):
        raise ValueError(f'not a Read State column: {lookup_name!r}')
    return replace(config, read_column=lookup_name)


def mark_read(library: Library, config: TierConfig, book_ids: Iterable[int], today: date) -> None:
    """Fill the Read State column of every book id, only where it is still empty."""
    ids = list(book_ids)
    datatype = library.column_types().get(config.read_column)
    if not ids or datatype not in READ_COLUMN_TYPES:
        return
    current = library.read_field(config.read_column, ids)
    if datatype == 'datetime':
        values = {book_id: today for book_id in ids if current.get(book_id) is None}
    else:  # 'bool'
        values = {book_id: True for book_id in ids if current.get(book_id) is not True}
    if values:
        library.write_field(config.read_column, values)


def mark_unread(library: Library, config: TierConfig, book_ids: Iterable[int]) -> None:
    """Clear Book Tier and Read State for every book id, one write per ready column."""
    ids = list(book_ids)
    if not ids:
        return
    cleared: dict[int, None] = {book_id: None for book_id in ids}
    if library.has_column(config.tier_column):
        library.write_field(config.tier_column, cleared)
    if column_ready(library, config):
        library.write_field(config.read_column, cleared)

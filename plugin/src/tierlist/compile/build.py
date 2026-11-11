"""Build Tier List Data from the books the library holds."""

from collections.abc import Iterable, Mapping
from dataclasses import replace
from datetime import date

from ..ports import Covers, Library
from ..tiers import MAX_STACK_DEPTH, MIN_STACK_DEPTH, TierConfig
from .covers import COVER_WIDTH
from .data import Book, Generated, Lane, TierListData
from .rows import Row, book_of, on_board, series_name
from .series import build_series, earliest, series_tier, stacks_for

READ_COLUMN_TYPES = ('datetime', 'bool')
DETAIL_FIELDS = ('authors', 'rating', 'tags', 'comments')


def compile_data(
    generated: Generated,
    library: Library,
    covers: Covers,
    fmt: str,
    config: TierConfig,
    book_ids: Iterable[int],
    overrides: Mapping[str, str],
) -> TierListData:
    """Read these books from the library, build their Tier List Data, then attach their covers."""
    ids = list(book_ids)
    titles = library.read_field('title', ids)
    tiers = library.read_field(config.tier_column, ids) if library.has_column(config.tier_column) else {}
    datatype = library.column_types().get(config.read_column)
    reads = library.read_field(config.read_column, ids) if datatype in READ_COLUMN_TYPES else {}
    series = library.read_field('series', ids)
    indexes = library.read_field('series_index', ids)
    column = config.series_total_column
    totals = library.read_field(column, ids) if library.column_types().get(column) == 'int' else {}
    extra = {name: library.read_field(name, ids) for name in DETAIL_FIELDS}
    rows = [
        Row(
            i,
            str(titles.get(i) or ''),
            tiers.get(i),
            reads.get(i),
            series.get(i),
            indexes.get(i),
            totals.get(i),
            **{name: values.get(i) for name, values in extra.items()},
        )
        for i in ids
    ]
    board = on_board(rows, datatype == 'bool', _overridden(config, overrides))
    shots = {row.id: cover for row in board if (cover := covers.cover(row.id, fmt, COVER_WIDTH)) is not None}
    colours = {book_id: cover.colour for book_id, cover in shots.items()}
    return replace(build(generated, config, board, datatype == 'bool', colours, overrides), covers=shots)


def count_series(library: Library, book_ids: Iterable[int]) -> int:
    """The number of distinct non-empty series among these books."""
    return len({value for value in library.read_field('series', list(book_ids)).values() if value})


def build(
    generated: Generated,
    config: TierConfig,
    board: Iterable[Row],
    read_is_bool: bool,
    colours: Mapping[int, str],
    overrides: Mapping[str, str],
) -> TierListData:
    """Resolve the board rows into Books and place them in ordered Lanes and Series Stacks."""
    known = {tier.id for tier in config.tiers}
    pairs = [(row, book_of(row, known, read_is_bool)) for row in board]
    books = tuple(sorted((book for _, book in pairs), key=lambda book: book.id))
    groups: dict[str, list[tuple[Row, Book]]] = {}
    standalone: list[Book] = []
    for row, book in pairs:
        name = series_name(row)
        if name is None:
            standalone.append(book)
        else:
            groups.setdefault(name, []).append((row, book))
    depth = max(MIN_STACK_DEPTH, min(MAX_STACK_DEPTH, config.stack_depth))
    resolved = {
        name: series_tier(name, [book.tier for _, book in group], config, overrides) for name, group in groups.items()
    }
    series = {
        name: build_series(
            {row.id: row.index for row, _ in group},
            (row.total for row, _ in group),
            depth,
            colours,
            resolved[name].override,
        )
        for name, group in groups.items()
    }
    stacks = {
        name: (resolved[name].tier_id, earliest([book.date_read for _, book in group if book.read]))
        for name, group in groups.items()
    }
    lanes = tuple(Lane(tier.id, _cards(standalone, tier.id), stacks_for(stacks, tier.id)) for tier in config.tiers)
    unranked = Lane(None, _cards(standalone, None), stacks_for(stacks, None))
    return TierListData(generated, config.tiers, (*lanes, unranked), books, series=series)


def _cards(books: list[Book], tier: str | None) -> tuple[int, ...]:
    matches = [book for book in books if book.tier == tier]
    matches.sort(key=lambda book: (book.date_read is None, book.date_read or date.min, book.title.casefold(), book.id))
    return tuple(book.id for book in matches)


def _overridden(config: TierConfig, overrides: Mapping[str, str]) -> set[str]:
    return {name for name, tier_id in overrides.items() if config.tier(tier_id) is not None}

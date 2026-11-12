"""Build Tier List Data from the books the library holds."""

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import replace
from typing import cast

from ..lane_order import UNRANKED_LANE, Place
from ..ports import Covers, Library
from ..tiers import TierConfig
from .covers import COVER_WIDTH, cover_thumbs
from .data import Book, Generated, Lane, LaneItem, TierListData
from .rows import Row, book_of, on_board, series_name
from .series import Rank, build_series, earliest, ordered_lane, series_tier

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
    order: Mapping[str, Sequence[Place]] | None = None,
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
    shots = cover_thumbs(covers, (row.id for row in board), fmt, COVER_WIDTH)
    colours = {book_id: cover.colour for book_id, cover in shots.items()}
    return replace(build(generated, config, board, datatype == 'bool', colours, overrides, order), covers=shots)


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
    order: Mapping[str, Sequence[Place]] | None = None,
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
    resolved = {
        name: series_tier(name, [book.tier for _, book in group], config, overrides) for name, group in groups.items()
    }
    series = {
        name: build_series(
            {row.id: row.index for row, _ in group},
            (row.total for row, _ in group),
            colours,
            resolved[name].override,
        )
        for name, group in groups.items()
    }
    read_dates = {name: earliest([book.date_read for _, book in group if book.read]) for name, group in groups.items()}
    members: dict[str, dict[Place, Rank]] = {tier.id: {} for tier in config.tiers}
    members[UNRANKED_LANE] = {}
    for name in groups:
        key = resolved[name].tier_id or UNRANKED_LANE
        members[key][('series', name)] = (read_dates[name], name, 0)
    for book in standalone:
        members[book.tier or UNRANKED_LANE][('book', book.id)] = (book.date_read, book.title, book.id)
    lanes = tuple(Lane(tier.id, _items(members[tier.id], _stored(order, tier.id))) for tier in config.tiers)
    unranked = Lane(None, _items(members[UNRANKED_LANE], _stored(order, None)))
    return TierListData(generated, config.tiers, (*lanes, unranked), books, series=series)


def _stored(order: Mapping[str, Sequence[Place]] | None, tier: str | None) -> Sequence[Place]:
    if order is None:
        return ()
    return order.get(tier or UNRANKED_LANE, ())


def _items(present: Mapping[Place, Rank], stored: Iterable[Place]) -> tuple[LaneItem, ...]:
    return tuple(_lane_item(place) for place in ordered_lane(present, stored))


def _lane_item(place: Place) -> LaneItem:
    kind, key = place
    return LaneItem(stack=cast(str, key)) if kind == 'series' else LaneItem(card=cast(int, key))


def _overridden(config: TierConfig, overrides: Mapping[str, str]) -> set[str]:
    return {name for name, tier_id in overrides.items() if config.tier(tier_id) is not None}

"""Tier List Data: the versioned, schema-defined payload the plugin embeds in the HTML."""

import base64
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Literal

from ..page_defaults import DEFAULT_PAGE_DEFAULTS, PageDefaults
from ..ports import Cover
from ..tiers import Tier
from .series import Series

SCHEMA_VERSION = 10

Scope = Literal['library', 'virtual_library', 'selection']


@dataclass(frozen=True)
class Generated:
    """When, where, and for which Compile Scope a compile ran."""

    at: datetime
    library_name: str
    scope: Scope
    plugin_version: str


@dataclass(frozen=True)
class Details:
    """What the detail panel shows beyond the board: authors, series and index, stars, tags, and the blurb."""

    authors: tuple[str, ...] = ()
    series: str | None = None
    series_index: str | None = None
    rating: float | None = None
    tags: tuple[str, ...] = ()
    blurb: str | None = None


@dataclass(frozen=True)
class Book:
    """One book on the board: its title, Book Tier, date read if any, whether it is read, and its details."""

    id: int
    title: str
    tier: str | None
    date_read: date | None
    read: bool = False
    details: Details = field(default_factory=Details)


@dataclass(frozen=True)
class LaneItem:
    """One item in a Lane, in Lane Order: a Stack's series name or a Card's book id, exactly one set."""

    stack: str | None = None
    card: int | None = None


@dataclass(frozen=True)
class Lane:
    """One row of the board: a Tier id, or None for the Unranked Lane, and its Stacks and Cards in order."""

    tier: str | None
    items: tuple[LaneItem, ...] = ()


@dataclass(frozen=True)
class CompileRequest:
    """The inputs one compile needs: the Compile Scope, the books, the library, and the plugin version."""

    scope: Scope
    book_ids: tuple[int, ...]
    library_name: str
    plugin_version: str


@dataclass(frozen=True)
class TierListData:
    """The compiled board: generation metadata, Tiers, Lanes, every book on the board, and its Series Stacks."""

    generated: Generated
    tiers: tuple[Tier, ...]
    lanes: tuple[Lane, ...]
    books: tuple[Book, ...]
    covers: Mapping[int, Cover] = field(default_factory=dict[int, Cover])
    series: Mapping[str, Series] = field(default_factory=dict[str, Series])
    page_defaults: PageDefaults = DEFAULT_PAGE_DEFAULTS

    def to_dict(self) -> dict[str, Any]:
        """Serialise to the schema's camelCase JSON shape."""
        return {
            'schemaVersion': SCHEMA_VERSION,
            'pageDefaults': self.page_defaults.to_dict(),
            'generated': {
                'at': self.generated.at.isoformat(),
                'libraryName': self.generated.library_name,
                'scope': self.generated.scope,
                'pluginVersion': self.generated.plugin_version,
            },
            'tiers': [
                {'id': tier.id, 'label': tier.label, 'colour': tier.colour, 'description': tier.description}
                for tier in self.tiers
            ],
            'lanes': [
                {
                    'tier': lane.tier,
                    'items': [
                        {'stack': item.stack} if item.stack is not None else {'card': str(item.card)}
                        for item in lane.items
                    ],
                }
                for lane in self.lanes
            ],
            'books': {
                str(book.id): {
                    'title': book.title,
                    'tier': book.tier,
                    'dateRead': None if book.date_read is None else book.date_read.isoformat(),
                    'read': book.read,
                    'authors': list(book.details.authors),
                    'series': book.details.series,
                    'seriesIndex': book.details.series_index,
                    'rating': book.details.rating,
                    'tags': list(book.details.tags),
                    'blurb': book.details.blurb,
                }
                for book in self.books
            },
            'series': {
                name: {
                    'colour': series.colour,
                    'positions': [
                        {'number': position.number, 'book': None if position.book is None else str(position.book)}
                        for position in series.positions
                    ],
                    'override': series.override,
                }
                for name, series in sorted(self.series.items())
            },
            'covers': {
                str(book_id): {
                    'src': f'data:image/{cover.format};base64,{base64.b64encode(cover.data).decode()}',
                    'colour': cover.colour,
                }
                for book_id, cover in sorted(self.covers.items())
            },
        }

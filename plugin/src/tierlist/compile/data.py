"""Tier List Data: the versioned, schema-defined payload the plugin embeds in the HTML."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from ..tiers import Tier

SCHEMA_VERSION = 1


@dataclass(frozen=True)
class Generated:
    """When, where, and for which Compile Scope a compile ran."""

    at: datetime
    library_name: str
    scope: str
    plugin_version: str


@dataclass(frozen=True)
class Book:
    """One book on the board: its title, Book Tier, and date read, if any."""

    id: int
    title: str
    tier: str | None
    date_read: date | None


@dataclass(frozen=True)
class Lane:
    """One row of the board: a Tier id, or None for the Unranked Lane, and its cards in order."""

    tier: str | None
    cards: tuple[int, ...]


@dataclass(frozen=True)
class CompileRequest:
    """The inputs one compile needs: the Compile Scope, the books, the library, and the plugin version."""

    scope: str
    book_ids: tuple[int, ...]
    library_name: str
    plugin_version: str


@dataclass(frozen=True)
class TierListData:
    """The compiled board: generation metadata, Tiers, Lanes, and every book on the board."""

    generated: Generated
    tiers: tuple[Tier, ...]
    lanes: tuple[Lane, ...]
    books: tuple[Book, ...]

    def to_dict(self) -> dict[str, Any]:
        """Serialise to the schema's camelCase JSON shape."""
        return {
            'schemaVersion': SCHEMA_VERSION,
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
            'lanes': [{'tier': lane.tier, 'cards': [str(card) for card in lane.cards]} for lane in self.lanes],
            'books': {
                str(book.id): {
                    'title': book.title,
                    'tier': book.tier,
                    'dateRead': None if book.date_read is None else book.date_read.isoformat(),
                }
                for book in self.books
            },
        }

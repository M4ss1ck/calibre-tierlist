"""The ports the calibre-free core needs, each with an adapter and an in-memory fake."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any, Protocol


class Library(Protocol):
    """The custom columns and books of the current library."""

    def has_column(self, lookup_name: str) -> bool:
        """True when the library has a single-valued Text custom column with this lookup name."""
        ...

    def column_types(self) -> Mapping[str, str]:
        """Every custom column lookup name mapped to its calibre datatype."""
        ...

    def read_field(self, lookup_name: str, book_ids: Iterable[int]) -> dict[int, object | None]:
        """The value of a column, or of the standard fields 'title', 'series', and 'series_index', for each book id;
        None where the field is empty."""
        ...

    def write_field(self, lookup_name: str, values: Mapping[int, object | None]) -> None:
        """Write a column for book ids, None clearing the field."""
        ...


class Prefs(Protocol):
    """Per-library plugin prefs, already namespaced by the adapter."""

    def get(self, key: str) -> Any:
        """Return the stored value, or None when the key is absent."""
        ...

    def set(self, key: str, value: Any) -> None:
        """Store a value for this library."""
        ...


@dataclass(frozen=True)
class Cover:
    """One book's cover thumbnail: its image format, bytes, and dominant colour ('#rrggbb')."""

    format: str
    data: bytes
    colour: str


class Covers(Protocol):
    """The cover thumbnails the host can produce for books."""

    def formats(self) -> frozenset[str]:
        """The image formats this host can encode (lowercase, e.g. 'webp')."""
        ...

    def cover(self, book_id: int, fmt: str, width: int) -> Cover | None:
        """The book's cover as a thumbnail `width` px wide encoded as `fmt`, with its dominant colour;
        None when the book has no cover."""
        ...


class NullCovers:
    """The Covers port for a host that cannot encode cover thumbnails."""

    def formats(self) -> frozenset[str]:
        return frozenset()

    def cover(self, book_id: int, fmt: str, width: int) -> Cover | None:
        return None


NULL_COVERS: Covers = NullCovers()

"""The ports the calibre-free core needs, each with an adapter and an in-memory fake."""

from collections.abc import Iterable, Mapping
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
        """The value of a column, or of the standard fields 'title' and 'series', for each book id;
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

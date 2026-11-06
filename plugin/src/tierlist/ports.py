"""The ports the calibre-free core needs, each with an adapter and an in-memory fake."""

from collections.abc import Mapping
from typing import Any, Protocol


class Library(Protocol):
    """The custom columns and books of the current library."""

    def has_column(self, lookup_name: str) -> bool:
        """True when the library has a custom column with this lookup name."""
        ...

    def write_text(self, lookup_name: str, values: Mapping[int, str | None]) -> None:
        """Write a Text column for book ids, None clearing the field."""
        ...


class Prefs(Protocol):
    """Per-library plugin prefs, already namespaced by the adapter."""

    def get(self, key: str) -> Any:
        """Return the stored value, or None when the key is absent."""
        ...

    def set(self, key: str, value: Any) -> None:
        """Store a value for this library."""
        ...

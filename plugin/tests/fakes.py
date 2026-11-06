"""In-memory Library and Prefs ports, so domain tests never touch calibre."""

from collections.abc import Iterable, Mapping


class FakeLibrary:
    """A Library port holding custom columns and their values in memory."""

    def __init__(self, columns: Iterable[str] = ('#tier',)) -> None:
        self.columns: set[str] = set(columns)
        self.values: dict[str, dict[int, str]] = {}
        self.writes = 0

    def has_column(self, lookup_name: str) -> bool:
        return lookup_name in self.columns

    def write_text(self, lookup_name: str, values: Mapping[int, str | None]) -> None:
        if lookup_name not in self.columns:
            raise KeyError(lookup_name)
        self.writes += 1
        column = self.values.setdefault(lookup_name, {})
        for book_id, value in values.items():
            if value is None:
                column.pop(book_id, None)
            else:
                column[book_id] = value


class FakePrefs:
    """A Prefs port backed by a plain dict."""

    def __init__(self, data: dict[str, object] | None = None) -> None:
        self.data: dict[str, object] = {} if data is None else data

    def get(self, key: str) -> object | None:
        return self.data.get(key)

    def set(self, key: str, value: object) -> None:
        self.data[key] = value

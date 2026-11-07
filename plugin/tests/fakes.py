"""In-memory Library and Prefs ports, so domain tests never touch calibre."""

import base64
from collections.abc import Iterable, Mapping

from tierlist.ports import Cover

STANDARD_FIELDS = ('title', 'series', 'series_index')
TINY_WEBP = base64.b64decode('UklGRhoAAABXRUJQVlA4TA0AAAAvAAAAEAcQERGIiP4HAA==')


class FakeLibrary:
    """A Library port holding custom columns and their values in memory."""

    def __init__(self, columns: Iterable[str] = ('#tier',), types: Mapping[str, str] | None = None) -> None:
        self.columns: set[str] = set(columns)
        self.types: dict[str, str] = dict(types or {})
        self.values: dict[str, dict[int, object]] = {}
        self.writes = 0

    def column_types(self) -> Mapping[str, str]:
        return {name: 'text' for name in self.columns} | self.types

    def has_column(self, lookup_name: str) -> bool:
        return self.column_types().get(lookup_name) == 'text'

    def read_field(self, lookup_name: str, book_ids: Iterable[int]) -> dict[int, object | None]:
        if lookup_name not in self.column_types() and lookup_name not in STANDARD_FIELDS:
            raise KeyError(lookup_name)
        column = self.values.get(lookup_name, {})
        return {book_id: column.get(book_id) for book_id in book_ids}

    def write_field(self, lookup_name: str, values: Mapping[int, object | None]) -> None:
        if lookup_name not in self.column_types():
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


class FakeCovers:
    """A Covers port where only the listed books have a tiny WebP thumbnail."""

    def __init__(
        self,
        formats: frozenset[str] = frozenset({'webp', 'jpeg'}),
        with_cover: Iterable[int] = (),
        colours: Mapping[int, str] | None = None,
    ) -> None:
        self._formats = formats
        self._with_cover = set(with_cover)
        self._colours = dict(colours or {})
        self.calls: list[tuple[int, str, int]] = []

    def formats(self) -> frozenset[str]:
        return self._formats

    def cover(self, book_id: int, fmt: str, width: int) -> Cover | None:
        self.calls.append((book_id, fmt, width))
        if book_id not in self._with_cover:
            return None
        return Cover(fmt, TINY_WEBP, self._colours.get(book_id, '#336699'))

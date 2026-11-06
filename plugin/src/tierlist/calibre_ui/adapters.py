"""calibre implementations of the Library, Prefs, and Covers ports."""

from collections.abc import Iterable, Mapping
from datetime import date, datetime, time
from typing import Any

from calibre.utils.date import local_tz

from ..app import TierList
from ..ports import Library, Prefs
from .covers import CalibreCovers


class CalibreLibrary(Library):
    """The current calibre library database, as the Library port."""

    def __init__(self, db: Any) -> None:
        self._db = db

    def has_column(self, lookup_name: str) -> bool:
        metadata = self._db.field_metadata
        if lookup_name not in metadata.custom_field_keys():
            return False
        column = metadata[lookup_name]
        return column['datatype'] == 'text' and not column['is_multiple']

    def column_types(self) -> Mapping[str, str]:
        metadata = self._db.field_metadata
        return {key: metadata[key]['datatype'] for key in metadata.custom_field_keys()}

    def read_field(self, lookup_name: str, book_ids: Iterable[int]) -> dict[int, object | None]:
        return {book_id: self._db.new_api.field_for(lookup_name, book_id) for book_id in book_ids}

    def write_field(self, lookup_name: str, values: Mapping[int, object | None]) -> None:
        converted = {book_id: _calibre_value(value) for book_id, value in values.items()}
        self._db.new_api.set_field(lookup_name, converted)


def _calibre_value(value: object | None) -> object | None:
    """Store a plain date at noon, the way calibre's date columns expect."""
    if isinstance(value, date) and not isinstance(value, datetime):
        return datetime.combine(value, time(12), tzinfo=local_tz)
    return value


class CalibrePrefs(Prefs):
    """The current library's namespaced plugin prefs, as the Prefs port."""

    def __init__(self, db: Any) -> None:
        self._db = db

    def get(self, key: str) -> Any:
        return self._db.prefs.get_namespaced('tierlist', key, None)

    def set(self, key: str, value: Any) -> None:
        self._db.prefs.set_namespaced('tierlist', key, value)


def tier_list(db: Any) -> TierList:
    """The facade over one calibre library database and its prefs."""
    return TierList(CalibreLibrary(db), CalibrePrefs(db), covers=CalibreCovers(db))

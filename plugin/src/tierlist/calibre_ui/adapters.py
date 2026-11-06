"""calibre implementations of the Library and Prefs ports."""

from collections.abc import Mapping
from typing import Any

from ..app import TierList
from ..ports import Library, Prefs


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

    def write_text(self, lookup_name: str, values: Mapping[int, str | None]) -> None:
        self._db.new_api.set_field(lookup_name, dict(values))


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
    return TierList(CalibreLibrary(db), CalibrePrefs(db))

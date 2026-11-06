"""A stand-in for calibre's main window: just what the Tier List action touches."""

from typing import Any

from calibre.gui2.keyboard import Manager
from qt.core import QMainWindow


class FakeModel:
    def __init__(self, db: Any) -> None:
        self.db = db
        self.refreshed: list[list[int]] = []

    def refresh_ids(self, ids: list[int]) -> None:
        self.refreshed.append(list(ids))


class FakeLibraryView:
    def __init__(self, db: Any, ids: list[int]) -> None:
        self._ids = ids
        self._model = FakeModel(db)

    def get_selected_ids(self) -> list[int]:
        return list(self._ids)

    def model(self) -> FakeModel:
        return self._model


class FakeGui(QMainWindow):
    def __init__(self, db: Any, ids: list[int]) -> None:
        super().__init__()
        self.keyboard = Manager(self)
        self.current_db = db
        self.library_view = FakeLibraryView(db, ids)

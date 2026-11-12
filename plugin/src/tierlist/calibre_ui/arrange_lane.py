"""One Lane in the Arrange View: a wrapping row of draggable covers, and the pool that loads them."""

import json
from collections.abc import Callable, Sequence
from typing import Any

from qt.core import (
    QAbstractItemView,
    QDrag,
    QListView,
    QListWidget,
    QListWidgetItem,
    QMimeData,
    QObject,
    QRunnable,
    QSize,
    Qt,
    QThreadPool,
    pyqtSignal,
)

from ..arrange import ArrangeItem

ITEM_MIME = 'application/x-tierlist-arrange-item'
ITEM_ROLE = Qt.ItemDataRole.UserRole
CELL_WIDTH, CELL_HEIGHT = 104, 150
ICON_WIDTH, ICON_HEIGHT = 80, 120

# What a Lane calls when an item is dropped there: kind, key, target Tier (None for Unranked), index.
DropHandler = Callable[[str, str | int, str | None, int], None]


class LaneList(QListWidget):
    """One Lane's wrapping row of covers; a drop is handed to the tab, not applied here."""

    def __init__(self, lane_tier: str | None, on_drop: DropHandler, parent: Any = None) -> None:
        super().__init__(parent)
        self.lane_tier = lane_tier
        self._on_drop = on_drop
        self.setViewMode(QListView.ViewMode.IconMode)
        self.setFlow(QListView.Flow.LeftToRight)
        self.setWrapping(True)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setMovement(QListView.Movement.Static)
        self.setGridSize(QSize(CELL_WIDTH, CELL_HEIGHT))
        self.setIconSize(QSize(ICON_WIDTH, ICON_HEIGHT))
        self.setSpacing(2)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        # setMovement(Static) turned the viewport's drops off, and drops land on the viewport:
        # the view itself ignores drag events, so without this every drop is refused.
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.fit()

    def add_item(self, item: ArrangeItem) -> QListWidgetItem:
        """Add one cover, remembering what a drop of it would move."""
        widget_item = QListWidgetItem(item.label, self)
        widget_item.setData(ITEM_ROLE, (item.kind, item.key))
        widget_item.setToolTip(item.label)
        widget_item.setSizeHint(QSize(CELL_WIDTH, CELL_HEIGHT))
        self.addItem(widget_item)
        return widget_item

    def fit(self) -> None:
        """Grow to as many wrapping rows as the items need at the current width."""
        columns = max(1, self.viewport().width() // CELL_WIDTH)
        rows = max(1, (self.count() + columns - 1) // columns)
        self.setFixedHeight(rows * CELL_HEIGHT + 8)

    def resizeEvent(self, event: Any) -> None:
        super().resizeEvent(event)
        self.fit()

    def startDrag(self, actions: Any) -> None:
        item = self.currentItem()
        if item is None:
            return
        kind, key = item.data(ITEM_ROLE)
        mime = QMimeData()
        mime.setData(ITEM_MIME, json.dumps({'kind': kind, 'key': key}).encode('utf-8'))
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event: Any) -> None:
        if event.mimeData().hasFormat(ITEM_MIME):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event: Any) -> None:
        if event.mimeData().hasFormat(ITEM_MIME):
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event: Any) -> None:
        if not event.mimeData().hasFormat(ITEM_MIME):
            super().dropEvent(event)
            return
        payload = json.loads(bytes(event.mimeData().data(ITEM_MIME)).decode('utf-8'))
        index = self.indexAt(event.position().toPoint()).row()
        self._on_drop(payload['kind'], payload['key'], self.lane_tier, self.count() if index < 0 else index)
        event.acceptProposedAction()


class Thumbnailer(QObject):
    """Loads small covers on a pool, off the GUI thread, the first cover these books have."""

    loaded = pyqtSignal(object, object, object)

    def __init__(self, thumbnail: Callable[[int], Any]) -> None:
        super().__init__()
        self._thumbnail = thumbnail
        self._pool = QThreadPool.globalInstance()

    def request(self, kind: str, key: str | int, books: Sequence[int]) -> None:
        """Ask for the first of these books' covers; `loaded` carries the bytes, or None."""
        self._pool.start(_ThumbJob(self._thumbnail, kind, key, tuple(books), self.loaded.emit))


class _ThumbJob(QRunnable):
    def __init__(
        self, thumbnail: Callable[[int], Any], kind: str, key: str | int, books: tuple[int, ...], done: Any
    ) -> None:
        super().__init__()
        self._thumbnail = thumbnail
        self._kind, self._key, self._books, self._done = kind, key, books, done

    def run(self) -> None:
        for book_id in self._books:
            cover = self._thumbnail(book_id)
            if cover is not None:
                self._done(self._kind, self._key, cover.data)
                return
        self._done(self._kind, self._key, None)

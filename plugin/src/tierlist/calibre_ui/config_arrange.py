"""The Arrange tab of Settings: the whole-library board as draggable Lanes of covers."""

from typing import Any, cast

from qt.core import QColor, QHBoxLayout, QIcon, QLabel, QListWidgetItem, QPixmap, QScrollArea, QVBoxLayout, QWidget

from ..arrange import ArrangeItem, Kind
from ..config_admin import ConfigAdmin
from ..tiers import Tier
from .adapters import config_admin
from .arrange_lane import LaneList, Thumbnailer

UNRANKED_COLOUR = '#808080'
Identity = tuple[str, str | int]


class ArrangeTab(QWidget):
    """The whole-library board as wrapping Lane rows; drops are staged until Settings saves."""

    def __init__(self, gui: Any, parent: Any = None) -> None:
        super().__init__(parent)
        self._admin: ConfigAdmin = config_admin(gui.current_db)
        self._staged = self._admin.arrange()
        self._dirty = False
        self._visible = False
        self._covers: dict[Identity, bytes | None] = {}
        self._items: dict[Identity, QListWidgetItem] = {}
        self._books: dict[Identity, tuple[int, ...]] = {}
        self._lanes: list[LaneList] = []
        self._loader = Thumbnailer(self._admin.thumbnail)
        self._loader.loaded.connect(self._on_cover)
        self._build()

    def _build(self) -> None:
        body = QWidget(self)
        column = QVBoxLayout(body)
        column.addWidget(QLabel(_('Drag covers between Lanes. Settings saves the new order when you press OK.'), body))
        for tier, items in self._staged.lanes():
            column.addWidget(self._header(tier, body))
            lane = LaneList(None if tier is None else tier.id, self._on_drop, body)
            self._lanes.append(lane)
            self._fill(lane, items)
            column.addWidget(lane)
        column.addStretch(1)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setWidget(body)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _header(self, tier: Tier | None, parent: QWidget) -> QWidget:
        header = QWidget(parent)
        row = QHBoxLayout(header)
        swatch = QLabel('', header)
        swatch.setFixedSize(16, 16)
        swatch.setStyleSheet(f'background-color: {tier.colour if tier else UNRANKED_COLOUR}; border-radius: 3px;')
        row.addWidget(swatch)
        row.addWidget(QLabel(tier.label if tier else _('Unranked'), header))
        row.addStretch(1)
        return header

    def _fill(self, lane: LaneList, items: tuple[ArrangeItem, ...]) -> None:
        for item in items:
            identity: Identity = (item.kind, item.key)
            self._books[identity] = item.books
            widget_item = lane.add_item(item)
            self._items[identity] = widget_item
            widget_item.setBackground(QColor(item.colour))
            if identity in self._covers:
                self._set_icon(widget_item, self._covers[identity])
            elif self._visible:
                self._request(identity)
        lane.fit()

    def _request(self, identity: Identity) -> None:
        kind, key = identity
        self._loader.request(kind, key, self._books[identity])

    def _set_icon(self, widget_item: QListWidgetItem, data: bytes | None) -> None:
        if data is None:
            return
        pixmap = QPixmap()
        if pixmap.loadFromData(data):
            widget_item.setIcon(QIcon(pixmap))

    def _on_cover(self, kind: str, key: str | int, data: bytes | None) -> None:
        identity: Identity = (kind, key)
        self._covers[identity] = data
        widget_item = self._items.get(identity)
        if widget_item is not None:
            self._set_icon(widget_item, data)

    def showEvent(self, event: Any) -> None:
        super().showEvent(event)
        if not self._visible:
            self._visible = True
            for identity in self._books:
                if identity not in self._covers:
                    self._request(identity)

    def drop(self, kind: Kind, key: str | int, target: str | None, index: int = -1) -> None:
        """Stage one drag, as a drop on a Lane translates it."""
        self._staged.move(kind, key, target, index)
        self._dirty = True
        self._refresh()

    def _on_drop(self, kind: str, key: str | int, target: str | None, index: int) -> None:
        self.drop(cast('Kind', kind), key, target, index)

    def _refresh(self) -> None:
        self._items.clear()
        self._books.clear()
        for lane, (_, items) in zip(self._lanes, self._staged.lanes(), strict=True):
            lane.clear()
            self._fill(lane, items)

    def save(self) -> None:
        """Write the staged drags, when there are any."""
        if self._dirty:
            self._admin.save_arrange(self._staged)

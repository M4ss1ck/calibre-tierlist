"""Integration test for the Arrange View's mouse: dragging a cover onto another Lane stages the move.

The drag runs the lane's real startDrag; only QDrag.exec, which needs a real pointer, is replaced
by delivering the drag events where Qt would: the widget under the point, else its nearest
ancestor that accepts drops (QWidgetWindow's findDnDTarget).

Run with ``calibre-debug -e plugin/itest/arrange_drag.py`` after installing the plugin into a
throwaway ``CALIBRE_CONFIG_DIRECTORY``. Prints ``ARRANGE DRAG OK`` and exits 0.
calibre runs Python with -OO, which strips ``assert``; use ``expect``.
"""

import sys
import tempfile
from typing import Any

from arrange import expect, library
from calibre.gui2 import Application
from calibre_plugins.tierlist.calibre_ui import arrange_lane
from calibre_plugins.tierlist.calibre_ui.adapters import tier_list
from calibre_plugins.tierlist.calibre_ui.settings_dialog import SettingsDialog
from fake_gui import FakeGui
from qt.core import (
    QApplication,
    QDragEnterEvent,
    QDragMoveEvent,
    QDropEvent,
    QEvent,
    QMouseEvent,
    QPoint,
    QPointF,
    Qt,
)

STARTED: list[Any] = []
TARGET: list[Any] = []


def dnd_target(widget: Any) -> Any:
    while widget is not None and not widget.acceptDrops():
        widget = widget.parentWidget()
    return widget


class FakeDrag:
    """Stands in for QDrag: exec delivers enter, move and drop on TARGET's first cover."""

    def __init__(self, source: Any) -> None:
        self.mime: Any = None

    def setMimeData(self, mime: Any) -> None:
        self.mime = mime

    def exec(self, actions: Any) -> Any:
        STARTED.append(self.mime)
        lane = TARGET[0]
        local = lane.visualItemRect(lane.item(0)).center()
        receiver = dnd_target(lane.viewport().childAt(local) or lane.viewport())
        if receiver is None:
            return Qt.DropAction.IgnoreAction
        point = receiver.mapFrom(lane.viewport(), local)
        buttons, mods = Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier
        enter = QDragEnterEvent(point, actions, self.mime, buttons, mods)
        QApplication.sendEvent(receiver, enter)
        if not enter.isAccepted():
            return Qt.DropAction.IgnoreAction
        QApplication.sendEvent(receiver, QDragMoveEvent(point, actions, self.mime, buttons, mods))
        drop = QDropEvent(QPointF(point), actions, self.mime, buttons, mods)
        QApplication.sendEvent(receiver, drop)
        return drop.dropAction() if drop.isAccepted() else Qt.DropAction.IgnoreAction


def mouse(target: Any, kind: Any, pos: QPoint, buttons: Any) -> None:
    button = Qt.MouseButton.LeftButton if kind != QEvent.Type.MouseMove else Qt.MouseButton.NoButton
    point = QPointF(pos)
    event = QMouseEvent(kind, point, target.mapToGlobal(point), button, buttons, Qt.KeyboardModifier.NoModifier)
    QApplication.sendEvent(target, event)
    QApplication.processEvents()


def press_and_move(lane: Any) -> None:
    """Press on the lane's first cover and move past the drag distance, as a user would."""
    viewport = lane.viewport()
    start = lane.visualItemRect(lane.item(0)).center()
    held = Qt.MouseButton.LeftButton
    mouse(viewport, QEvent.Type.MouseButtonPress, start, held)
    step = QApplication.startDragDistance() + 5
    for offset in (step, step * 2, step * 3):
        mouse(viewport, QEvent.Type.MouseMove, start + QPoint(offset, offset), held)
    mouse(viewport, QEvent.Type.MouseButtonRelease, start + QPoint(step * 3, step * 3), Qt.MouseButton.NoButton)


def check_drag(path: str) -> None:
    db, _, other, _ = library(path)
    tier_list(db).set_book_tier([other], 'a')
    original = arrange_lane.QDrag
    arrange_lane.QDrag = FakeDrag
    try:
        dialog = SettingsDialog(FakeGui(db, []), tab='arrange')
        dialog.show()
        QApplication.processEvents()
        tab: Any = dialog.widget.arrange
        lane = next(lane for lane in tab._lanes if lane.count())
        target = next(other for other in tab._lanes if other.count() and other is not lane)
        TARGET.append(target)
        moved = lane.item(0).data(arrange_lane.ITEM_ROLE)
        expect(lane.isVisible() and lane.viewport().width() > 0, 'the lane is not laid out')
        expect(bool(lane.item(0).flags() & Qt.ItemFlag.ItemIsDragEnabled), 'covers are not drag enabled')
        press_and_move(lane)
        expect(len(STARTED) == 1, f'pressing a cover and moving started {len(STARTED)} drags, not one')
        staged = [item.data(arrange_lane.ITEM_ROLE) for item in (target.item(i) for i in range(target.count()))]
        expect(staged[:1] == [moved], f'the drop did not stage {moved} first in its Lane: {staged}')
        expect(tab._dirty, 'the drop left nothing to save')
        dialog.reject()
    finally:
        arrange_lane.QDrag = original
        db.close()


def main() -> int:
    Application([])
    with tempfile.TemporaryDirectory() as tmp:
        check_drag(tmp + '/drag')
    print('ARRANGE DRAG OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())

"""The column mapping combos and the Orphaned Overrides list in the config dialog."""

from collections.abc import Callable, Mapping, Sequence
from typing import Any

from qt.core import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..config_admin import ConfigAdmin


def fill_column_combo(
    combo: QComboBox,
    types: Mapping[str, str],
    datatypes: tuple[str, ...],
    current: str,
    none_label: str | None = None,
) -> None:
    """Fill a combo with this library's columns of these datatypes, keeping `current` selected even when absent."""
    combo.clear()
    if none_label is not None:
        combo.addItem(none_label, '')
    for lookup in sorted(lookup for lookup, datatype in types.items() if datatype in datatypes):
        combo.addItem(lookup, lookup)
    index = combo.findData(current) if current else 0
    if current and index < 0:
        combo.insertItem(0, current, current)
        index = 0
    combo.setCurrentIndex(max(index, 0))


class OrphanPanel(QWidget):
    """The Orphaned Overrides list; Reattach and Delete apply immediately."""

    def __init__(self, admin: ConfigAdmin, series_names: Callable[[], Sequence[str]], parent: Any = None) -> None:
        super().__init__(parent)
        self._admin = admin
        self._series_names = series_names
        self.list = QListWidget(self)
        self.list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.empty = QLabel(_('No orphaned series overrides'), self)
        buttons = QHBoxLayout()
        for text, slot in ((_('Reattach…'), self.reattach), (_('Delete'), self.delete)):
            button = QPushButton(text, self)
            button.clicked.connect(slot)
            buttons.addWidget(button)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(_('Orphaned Overrides'), self))
        layout.addWidget(self.empty)
        layout.addWidget(self.list)
        layout.addLayout(buttons)
        self.refresh()

    def refresh(self) -> None:
        """Reload the list from the stored Overrides."""
        names = self._admin.orphans()
        self.list.clear()
        self.list.addItems(names)
        self.empty.setVisible(not names)
        self.list.setVisible(bool(names))

    def reattach(self) -> None:
        """Attach the selected Orphaned Override to a series this library has."""
        selected = self.selected()
        names = list(self._series_names())
        if not selected or not names:
            return
        series, accepted = QInputDialog.getItem(
            self, _('Reattach Override'), _('Attach this Override to series:'), names, 0, False
        )
        if accepted and series:
            self._admin.reattach_orphan(selected[0], series)
            self.refresh()

    def delete(self) -> None:
        """Drop the selected Orphaned Overrides."""
        self._admin.delete_orphans(self.selected())
        self.refresh()

    def selected(self) -> list[str]:
        """The names of the selected Orphaned Overrides."""
        return [item.text() for item in self.list.selectedItems()]

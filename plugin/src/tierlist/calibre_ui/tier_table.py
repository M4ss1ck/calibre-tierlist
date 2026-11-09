"""The Tier table in the config dialog: one row per Tier, with Add, Remove, and reordering."""

from typing import Any

from qt.core import QColor, QColorDialog, QPushButton, Qt, QTableWidget, QTableWidgetItem

from ..tiers import Tier

ID, LABEL, COLOUR, DESCRIPTION = range(4)
NEW_COLOUR = '#c0c0c0'


class SwatchButton(QPushButton):
    """A Tier colour swatch: shows the #rrggbb it stores and picks a new one when clicked."""

    def __init__(self, colour: str, parent: Any = None) -> None:
        super().__init__(colour, parent)
        self.set_colour(colour)
        self.clicked.connect(self.choose)

    def set_colour(self, colour: str) -> None:
        """Show this colour, and store it as the button's text."""
        self.setText(colour)
        self.setStyleSheet(f'background-color: {colour};')

    def choose(self) -> None:
        """Ask for a colour and keep it when the user accepts one."""
        chosen = QColorDialog.getColor(QColor(self.text()), self, _('Tier colour'))
        if chosen.isValid():
            self.set_colour(chosen.name())


class TierTable(QTableWidget):
    """The ordered Tiers as table rows: id, label, colour swatch, and description."""

    def __init__(self, parent: Any = None) -> None:
        super().__init__(0, 4, parent)
        self.setHorizontalHeaderLabels([_('Id'), _('Label'), _('Colour'), _('Description')])
        self.verticalHeader().setVisible(False)
        self._new: set[int] = set()

    def set_tiers(self, tiers: tuple[Tier, ...]) -> None:
        """Replace every row with these Tiers; none of them is a new row."""
        self.setRowCount(0)
        self._new.clear()
        for tier in tiers:
            self._append(tier)

    def tiers(self) -> tuple[Tier, ...]:
        """The Tiers the rows currently hold, in order."""
        return tuple(
            Tier(
                id=self.text_at(row, ID),
                label=self.text_at(row, LABEL),
                colour=self.text_at(row, COLOUR),
                description=self.text_at(row, DESCRIPTION),
            )
            for row in range(self.rowCount())
        )

    def add(self) -> int:
        """Append a Tier with a generated unique id, make its id editable, and select it."""
        row = self._append(Tier(self._next_id(), '', NEW_COLOUR))
        self._new.add(row)
        item = self.item(row, ID)
        if item is not None:
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.selectRow(row)
        return row

    def remove(self, row: int) -> None:
        """Drop one row, keeping the other new rows' flags."""
        self.removeRow(row)
        self._new = {new - 1 if new > row else new for new in self._new if new != row}

    def move(self, row: int, offset: int) -> int:
        """Swap a row with its neighbour, and return the row's new index."""
        target = row + offset
        if not 0 <= target < self.rowCount():
            return row
        tiers = list(self.tiers())
        tiers[row], tiers[target] = tiers[target], tiers[row]
        new = [(target if old == row else row if old == target else old) for old in self._new]
        self.set_tiers(tuple(tiers))
        for moved in new:
            self._new.add(moved)
            item = self.item(moved, ID)
            if item is not None:
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.selectRow(target)
        return target

    def selected_row(self) -> int | None:
        """The current row, or None when no row is selected."""
        row = self.currentRow()
        return row if row >= 0 else None

    def tier_id(self, row: int) -> str:
        """The id this row holds."""
        return self.text_at(row, ID)

    def text_at(self, row: int, column: int) -> str:
        """The text one cell shows, the swatch button's colour for the colour cell."""
        if column == COLOUR:
            widget = self.cellWidget(row, COLOUR)
            return widget.text() if widget is not None else ''
        item = self.item(row, column)
        return item.text() if item is not None else ''

    def _append(self, tier: Tier) -> int:
        row = self.rowCount()
        self.insertRow(row)
        item = QTableWidgetItem(tier.id)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.setItem(row, ID, item)
        self.setItem(row, LABEL, QTableWidgetItem(tier.label))
        self.setItem(row, DESCRIPTION, QTableWidgetItem(tier.description))
        self.setCellWidget(row, COLOUR, SwatchButton(tier.colour, self))
        return row

    def _next_id(self) -> str:
        used = {self.text_at(row, ID) for row in range(self.rowCount())}
        number = 1
        while f't{number}' in used:
            number += 1
        return f't{number}'

"""Layout pieces for the config dialog: a row of buttons and the column mapping form."""

from collections.abc import Callable, Sequence
from typing import Any

from qt.core import QComboBox, QFormLayout, QHBoxLayout, QPushButton, QSpinBox, QWidget


def button_row(parent: QWidget, buttons: Sequence[tuple[str, Callable[[], Any]]]) -> QHBoxLayout:
    """A horizontal row of buttons, each connected to its handler."""
    row = QHBoxLayout()
    for text, slot in buttons:
        button = QPushButton(text, parent)
        button.clicked.connect(slot)
        row.addWidget(button)
    return row


def mapping_form(combos: Sequence[tuple[str, QComboBox]], depth: QSpinBox) -> QFormLayout:
    """The column mapping combos and the Stack depth spin box, labelled."""
    form = QFormLayout()
    for label, combo in combos:
        form.addRow(label, combo)
    form.addRow(_('Stack depth'), depth)
    return form

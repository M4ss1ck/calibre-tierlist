"""Layout pieces for the config dialog: a row of buttons and the column mapping form."""

from collections.abc import Callable, Sequence
from typing import Any

from qt.core import QComboBox, QFormLayout, QHBoxLayout, QPushButton, QWidget


def button_row(parent: QWidget, buttons: Sequence[tuple[str, Callable[[], Any]]]) -> QHBoxLayout:
    """A horizontal row of buttons, each connected to its handler."""
    row = QHBoxLayout()
    for text, slot in buttons:
        button = QPushButton(text, parent)
        button.clicked.connect(slot)
        row.addWidget(button)
    return row


def mapping_form(combos: Sequence[tuple[str, QComboBox]]) -> QFormLayout:
    """The column mapping combos, labelled."""
    form = QFormLayout()
    for label, combo in combos:
        form.addRow(label, combo)
    return form

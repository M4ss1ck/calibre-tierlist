"""Layout helpers for the Page tab: right-aligned forms, and combos carrying the contract value as item data."""

from collections.abc import Sequence

from qt.core import QComboBox, QFormLayout, QGroupBox, Qt, QWidget


def right_form(box: QGroupBox) -> QFormLayout:
    """A form layout for this group box, with its labels right-aligned."""
    form = QFormLayout()
    form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
    box.setLayout(form)
    return form


def choice_combo(parent: QWidget, choices: Sequence[tuple[str, str]]) -> QComboBox:
    """A combo showing each label, with its contract value as item data."""
    combo = QComboBox(parent)
    for value, label in choices:
        combo.addItem(label, value)
    return combo

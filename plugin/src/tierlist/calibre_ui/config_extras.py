"""The column mapping combo helper of the config dialog."""

from collections.abc import Mapping

from qt.core import QComboBox


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

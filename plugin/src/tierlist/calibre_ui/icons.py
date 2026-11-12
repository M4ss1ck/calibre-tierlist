"""The plugin's icons: its toolbar and context menu icon, and a swatch per Tier colour."""

from typing import Any

from qt.core import QColor, QIcon, QPixmap

ICON_PATH = 'images/icon.png'
SWATCH_SIZE = 16


def plugin_icon(plugin_name: str) -> Any:
    """The icon shipped in the zip; calibre's `get_icons` reads it from there."""
    return get_icons(ICON_PATH, plugin_name)


def tier_swatch(colour: str) -> QIcon:
    """A square of a Tier's colour, so menu items read like the board's Lanes."""
    pixmap = QPixmap(SWATCH_SIZE, SWATCH_SIZE)
    pixmap.fill(QColor(colour))
    return QIcon(pixmap)

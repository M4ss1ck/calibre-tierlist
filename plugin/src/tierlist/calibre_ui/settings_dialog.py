"""The Settings dialog the Tier List menu opens: the tabbed config widget with OK and Cancel."""

from typing import Any

from calibre.gui2 import gprefs
from qt.core import QDialog, QDialogButtonBox, QSize, QVBoxLayout

from .config_widget import ConfigWidget

load_translations()

GEOMETRY_KEY = 'tierlist-settings-dialog'
DEFAULT_SIZE = QSize(960, 720)


class SettingsDialog(QDialog):
    """Hosts the config widget for the current library; OK validates then saves, Cancel writes nothing."""

    def __init__(self, gui: Any, parent: Any = None, tab: str | None = None) -> None:
        super().__init__(parent or gui)
        self.setWindowTitle(_('Tier List Settings'))
        self.widget = ConfigWidget(gui)
        if tab is not None:
            self.widget.select(tab)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(self.widget)
        layout.addWidget(buttons)
        if not self.restore_geometry(gprefs, GEOMETRY_KEY):
            self.resize(self._default_size())

    def _default_size(self) -> QSize:
        """Room for the Tiers table and the Arrange board, never larger than the screen."""
        size = self.sizeHint().expandedTo(DEFAULT_SIZE)
        screen = self.screen()
        if screen is not None:
            size = size.boundedTo(screen.availableGeometry().size() * 0.9)
        return size

    def done(self, result: int) -> None:
        """Remember the size the user left, whether they pressed OK or Cancel."""
        self.save_geometry(gprefs, GEOMETRY_KEY)
        super().done(result)

    def accept(self) -> None:
        """Save and close when the widget holds a usable config; stay open otherwise."""
        if self.widget.validate():
            self.widget.save()
            super().accept()

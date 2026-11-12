"""The Settings dialog the Tier List menu opens: the tabbed config widget with OK and Cancel."""

from typing import Any

from qt.core import QDialog, QDialogButtonBox, QVBoxLayout

from .config_widget import ConfigWidget

load_translations()


class SettingsDialog(QDialog):
    """Hosts the config widget for the current library; OK validates then saves, Cancel writes nothing."""

    def __init__(self, gui: Any, parent: Any = None) -> None:
        super().__init__(parent or gui)
        self.setWindowTitle(_('Tier List Settings'))
        self.widget = ConfigWidget(gui)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(self.widget)
        layout.addWidget(buttons)

    def accept(self) -> None:
        """Save and close when the widget holds a usable config; stay open otherwise."""
        if self.widget.validate():
            self.widget.save()
            super().accept()

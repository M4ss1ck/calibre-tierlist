"""The Backup tab of Settings: importing and exporting Tier Config JSON."""

from typing import Any

from qt.core import QVBoxLayout, QWidget

from ..config_admin import ConfigAdmin
from .config_form import button_row
from .config_io import confirm_import, export_config, import_config
from .config_tiers import TiersTab


class BackupTab(QWidget):
    """The Import JSON… and Export JSON… buttons; an import only loads the Tiers tab until Settings is saved."""

    def __init__(self, admin: ConfigAdmin, tiers: TiersTab, parent: Any = None) -> None:
        super().__init__(parent)
        self._admin = admin
        self._tiers = tiers
        layout = QVBoxLayout(self)
        layout.addLayout(
            button_row(
                self,
                ((_('Import JSON…'), self.import_json), (_('Export JSON…'), self.export_json)),
            )
        )

    def import_json(self) -> None:
        """Load a JSON Tier Config's Tiers into the Tiers tab; the column mapping and save come later."""
        config = import_config(self, self._admin)
        if config is not None and confirm_import(self, self._admin, self._tiers.table.tiers(), config):
            self._tiers.load_tiers(config)

    def export_json(self) -> None:
        """Write the Tier Config the widgets currently show to a JSON file."""
        export_config(self, self._tiers.build_config())

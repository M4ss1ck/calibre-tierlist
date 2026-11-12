"""The Backup tab of Settings: importing and exporting Settings JSON."""

from typing import Any

from qt.core import QCheckBox, QVBoxLayout, QWidget

from ..config_admin import ConfigAdmin
from ..settings_export import SettingsExport
from .config_form import button_row
from .config_io import confirm_import, confirm_replace, export_settings, import_settings
from .config_page import PageTab
from .config_tiers import TiersTab


class BackupTab(QWidget):
    """The Import and Export Settings buttons, an opt-in for Overrides and Lane Order, and a staged import."""

    def __init__(self, admin: ConfigAdmin, tiers: TiersTab, page: PageTab, parent: Any = None) -> None:
        super().__init__(parent)
        self._admin = admin
        self._tiers = tiers
        self._page = page
        self._imported: SettingsExport | None = None
        self.include = QCheckBox(_('Include series Overrides and Lane Order'), self)
        layout = QVBoxLayout(self)
        layout.addLayout(
            button_row(
                self,
                ((_('Import JSON…'), self.import_json), (_('Export JSON…'), self.export_json)),
            )
        )
        layout.addWidget(self.include)

    def import_json(self) -> None:
        """Load a Settings Export's sections into the tabs; the import is written when Settings saves."""
        export = import_settings(self, self._admin)
        if export is None:
            return
        if export.tier_config is not None:
            shown = self._tiers.table.tiers()
            if not confirm_import(self, self._admin, shown, export.tier_config):
                return
        if not confirm_replace(self, export):
            return
        if export.tier_config is not None:
            self._tiers.load_tiers(export.tier_config)
        if export.page_defaults is not None:
            self._page.load(export.page_defaults)
        self._imported = export

    def export_json(self) -> None:
        """Write the settings the widgets currently show to a JSON file."""
        config, defaults = self._tiers.build_config(), self._page.build_defaults()
        export_settings(self, self._admin, config, defaults, self.include.isChecked())

    def apply_import(self) -> None:
        """Write the imported Overrides and Lane Order, when the import carried any."""
        if self._imported is not None:
            self._admin.apply_import(self._imported)
            self._tiers.orphans.refresh()
            self._imported = None

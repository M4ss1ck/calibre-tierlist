"""The Tiers tab of Settings: the Tier table, the column mapping, and the Orphaned Overrides."""

from typing import Any

from qt.core import QComboBox, QVBoxLayout, QWidget

from ..compile import READ_COLUMN_TYPES
from ..config_admin import ConfigAdmin
from ..tiers import TierConfig
from .config_extras import OrphanPanel, fill_column_combo
from .config_form import button_row, mapping_form
from .config_io import confirm_remove
from .tier_table import TierTable

TOTAL_COLUMN_TYPES = ('int',)


class TiersTab(QWidget):
    """One library's Tiers, their columns and its Orphaned Overrides."""

    def __init__(self, admin: ConfigAdmin, parent: Any = None) -> None:
        super().__init__(parent)
        self.admin = admin
        self.table = TierTable(self)
        self.tier_column = QComboBox(self)
        self.read_column = QComboBox(self)
        self.total_column = QComboBox(self)
        self.orphans = OrphanPanel(admin, admin.series_names, self)
        self._build_layout()
        self.load(admin.tier_config())

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addLayout(
            button_row(
                self,
                (
                    (_('Add'), self.table.add),
                    (_('Remove'), self.remove_tier),
                    (_('Move up'), self.move_up),
                    (_('Move down'), self.move_down),
                ),
            )
        )
        layout.addLayout(
            mapping_form(
                (
                    (_('Tier column'), self.tier_column),
                    (_('Read column'), self.read_column),
                    (_('Series total column'), self.total_column),
                ),
            )
        )
        layout.addWidget(self.orphans)

    def remove_tier(self) -> None:
        """Remove the selected Tier, asking first when books still hold it."""
        row = self.table.selected_row()
        if row is None:
            return
        if confirm_remove(self, self.admin.book_count(self.table.tier_id(row))):
            self.table.remove(row)

    def move_up(self) -> None:
        """Move the selected Tier one row up."""
        self._move(-1)

    def move_down(self) -> None:
        """Move the selected Tier one row down."""
        self._move(1)

    def _move(self, offset: int) -> None:
        row = self.table.selected_row()
        if row is not None:
            self.table.move(row, offset)

    def build_config(self) -> TierConfig:
        """The Tier Config the widgets currently show."""
        return TierConfig(
            tiers=self.table.tiers(),
            tier_column=self.tier_column.currentData(),
            read_column=self.read_column.currentData(),
            series_total_column=self.total_column.currentData() or '',
        )

    def load(self, config: TierConfig) -> None:
        """Show this Tier Config, column mapping included."""
        self.load_tiers(config)
        types = self.admin.column_types()
        fill_column_combo(self.tier_column, types, ('text',), config.tier_column)
        fill_column_combo(self.read_column, types, READ_COLUMN_TYPES, config.read_column)
        fill_column_combo(self.total_column, types, TOTAL_COLUMN_TYPES, config.series_total_column, _('None'))

    def load_tiers(self, config: TierConfig) -> None:
        """Show this Tier Config's Tiers only, leaving the column mapping alone."""
        self.table.set_tiers(config.tiers)

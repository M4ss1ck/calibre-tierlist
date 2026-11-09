"""The Tier Config dialog: the Tier table, column mapping, JSON import/export, and Orphaned Overrides."""

from typing import Any

from calibre.gui2 import error_dialog
from qt.core import QComboBox, QLabel, QSpinBox, QVBoxLayout, QWidget

from ..compile import READ_COLUMN_TYPES
from ..config_admin import ConfigAdmin
from ..tiers import MAX_STACK_DEPTH, MIN_STACK_DEPTH, TierConfig, TierConfigError, validate
from .adapters import config_admin
from .config_extras import OrphanPanel, fill_column_combo
from .config_form import button_row, mapping_form
from .config_io import confirm_import, confirm_remove, export_config, import_config
from .tier_table import TierTable

load_translations()

TOTAL_COLUMN_TYPES = ('int',)


class ConfigWidget(QWidget):
    """Preferences > Plugins > Tier List > Customize: edits one library's Tier Config."""

    def __init__(self, gui: Any) -> None:
        super().__init__()
        self.gui = gui
        self.admin: ConfigAdmin = config_admin(gui.current_db)
        self.table = TierTable(self)
        self.depth = QSpinBox(self)
        self.depth.setRange(MIN_STACK_DEPTH, MAX_STACK_DEPTH)
        self.tier_column = QComboBox(self)
        self.read_column = QComboBox(self)
        self.total_column = QComboBox(self)
        self.orphans = OrphanPanel(self.admin, self.admin.series_names, self)
        self._build_layout()
        self._load(self.admin.tier_config())

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(_('Tiers'), self))
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
                self.depth,
            )
        )
        layout.addLayout(
            button_row(
                self,
                ((_('Import JSON…'), self.import_json), (_('Export JSON…'), self.export_json)),
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

    def import_json(self) -> None:
        """Load a JSON Tier Config's Tiers into the widgets; the column mapping and save come later."""
        config = import_config(self, self.admin)
        if config is not None and confirm_import(self, self.admin, self.table.tiers(), config):
            self._load_tiers(config)

    def export_json(self) -> None:
        """Write the Tier Config the widgets currently show to a JSON file."""
        export_config(self, self.build_config())

    def build_config(self) -> TierConfig:
        """The Tier Config the widgets currently show."""
        return TierConfig(
            tiers=self.table.tiers(),
            tier_column=self.tier_column.currentData(),
            read_column=self.read_column.currentData(),
            stack_depth=self.depth.value(),
            series_total_column=self.total_column.currentData() or '',
        )

    def validate(self) -> bool:
        """True when the widgets hold a usable Tier Config; otherwise show why they do not."""
        try:
            validate(self.build_config())
        except TierConfigError as exc:
            error_dialog(self, _('Tier List'), str(exc), show=True)
            return False
        return True

    def save(self) -> None:
        """Store the Tier Config the widgets show, then refresh the library view and Tier menu."""
        self.admin.save(self.build_config())
        changed = getattr(self.gui, 'saved_searches_changed', None)
        if callable(changed):
            changed()
        actions: Any = getattr(self.gui, 'iactions', None) or {}
        action: Any = actions.get('Tier List')
        if action is not None:
            action.rebuild_menu()

    def _load(self, config: TierConfig) -> None:
        self._load_tiers(config)
        types = self.admin.column_types()
        fill_column_combo(self.tier_column, types, ('text',), config.tier_column)
        fill_column_combo(self.read_column, types, READ_COLUMN_TYPES, config.read_column)
        fill_column_combo(self.total_column, types, TOTAL_COLUMN_TYPES, config.series_total_column, _('None'))

    def _load_tiers(self, config: TierConfig) -> None:
        self.table.set_tiers(config.tiers)
        self.depth.setValue(config.stack_depth)

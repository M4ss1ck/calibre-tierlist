"""The Settings widget: the Tiers and Backup tabs, shared by Customize and the Tier List menu."""

from typing import Any

from calibre.gui2 import error_dialog
from qt.core import QTabWidget

from ..config_admin import ConfigAdmin
from ..tiers import TierConfig, TierConfigError, validate
from .adapters import config_admin
from .config_backup import BackupTab
from .config_page import PageTab
from .config_tiers import TiersTab

load_translations()


class ConfigWidget(QTabWidget):
    """One library's Settings: a tab per part of the config, shared by Customize and the Settings dialog."""

    def __init__(self, gui: Any) -> None:
        super().__init__()
        self.gui = gui
        self.admin: ConfigAdmin = config_admin(gui.current_db)
        self.tiers = TiersTab(self.admin, self)
        self.page = PageTab(self.admin, self)
        self.backup = BackupTab(self.admin, self.tiers, self)
        self.addTab(self.tiers, _('Tiers'))
        self.addTab(self.page, _('Page'))
        self.addTab(self.backup, _('Backup'))

    def build_config(self) -> TierConfig:
        """The Tier Config the widgets currently show."""
        return self.tiers.build_config()

    def validate(self) -> bool:
        """True when the widgets hold a usable Tier Config; otherwise show why they do not."""
        try:
            validate(self.build_config())
        except TierConfigError as exc:
            error_dialog(self, _('Tier List'), str(exc), show=True)
            return False
        return True

    def save(self) -> None:
        """Store the Tier Config and Page Defaults the widgets show, then refresh the library view and Tier menu."""
        self.admin.save(self.build_config())
        self.admin.save_page_defaults(self.page.build_defaults())
        changed = getattr(self.gui, 'saved_searches_changed', None)
        if callable(changed):
            changed()
        actions: Any = getattr(self.gui, 'iactions', None) or {}
        action: Any = actions.get('Tier List')
        if action is not None:
            action.rebuild_menu()

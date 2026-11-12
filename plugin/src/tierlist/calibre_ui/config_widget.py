"""The Settings widget: the Tiers, Page, Arrange and Export tabs, shared by Customize and the Tier List menu."""

from typing import Any

from calibre.gui2 import error_dialog
from qt.core import QTabWidget, QWidget

from ..config_admin import ConfigAdmin
from ..tiers import TierConfig, TierConfigError, validate
from .adapters import config_admin
from .config_arrange import ArrangeTab
from .config_export import ExportTab
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
        self.arrange = ArrangeTab(gui, self)
        self.export = ExportTab(self.admin, self.tiers, self.page, self)
        self.addTab(self.tiers, _('Tiers'))
        self.addTab(self.page, _('Page'))
        self.addTab(self.arrange, _('Arrange'))
        self.addTab(self.export, _('Export'))

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

    def select(self, name: str) -> None:
        """Show the tab held by this attribute, when the widget has one."""
        widget = getattr(self, name, None)
        if isinstance(widget, QWidget):
            self.setCurrentWidget(widget)

    def save(self) -> None:
        """Store the Tier Config, Page Defaults, and staged Arrange drops, then refresh the library view and menu."""
        self.admin.save(self.build_config())
        self.admin.save_page_defaults(self.page.build_defaults())
        self.arrange.save()
        self.export.apply_import()
        changed = getattr(self.gui, 'saved_searches_changed', None)
        if callable(changed):
            changed()
        actions: Any = getattr(self.gui, 'iactions', None) or {}
        action: Any = actions.get('Tier List')
        if action is not None:
            action.rebuild_menu()

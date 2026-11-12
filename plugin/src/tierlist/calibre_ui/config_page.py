"""The Page tab of Settings: the Page Defaults a compiled page opens with."""

from typing import Any

from qt.core import QCheckBox, QComboBox, QFormLayout, QLineEdit, QVBoxLayout, QWidget

from ..config_admin import ConfigAdmin
from ..page_defaults import THEMES, PageDefaults

THEME_LABELS = {'system': 'System', 'light': 'Light', 'dark': 'Dark'}


class PageTab(QWidget):
    """One library's Page Defaults: theme, title, Unranked Lane label, and the three header switches."""

    def __init__(self, admin: ConfigAdmin, parent: Any = None) -> None:
        super().__init__(parent)
        self.theme = QComboBox(self)
        for theme in THEMES:
            self.theme.addItem(_(THEME_LABELS[theme]), theme)
        self.title = QLineEdit(self)
        self.unranked = QLineEdit(self)
        self.show_unranked = QCheckBox(_('Show the Unranked Lane'), self)
        self.show_counts = QCheckBox(_('Show the book and series counts'), self)
        self.show_library = QCheckBox(_('Show the library name'), self)
        form = QFormLayout()
        form.addRow(_('Theme'), self.theme)
        form.addRow(_('Title'), self.title)
        form.addRow(_('Unranked Lane label'), self.unranked)
        form.addRow('', self.show_unranked)
        form.addRow('', self.show_counts)
        form.addRow('', self.show_library)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        self.load(admin.page_defaults())

    def build_defaults(self) -> PageDefaults:
        """The Page Defaults the widgets currently show."""
        return PageDefaults(
            theme=self.theme.currentData(),
            title=self.title.text(),
            unranked_label=self.unranked.text(),
            show_unranked=self.show_unranked.isChecked(),
            show_counts=self.show_counts.isChecked(),
            show_library=self.show_library.isChecked(),
        )

    def load(self, defaults: PageDefaults) -> None:
        """Show these Page Defaults."""
        self.theme.setCurrentIndex(max(self.theme.findData(defaults.theme), 0))
        self.title.setText(defaults.title)
        self.unranked.setText(defaults.unranked_label)
        self.show_unranked.setChecked(defaults.show_unranked)
        self.show_counts.setChecked(defaults.show_counts)
        self.show_library.setChecked(defaults.show_library)

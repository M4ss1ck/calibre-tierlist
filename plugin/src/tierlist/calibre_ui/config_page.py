"""The Page tab of Settings: the Page Defaults a compiled page opens with, in four groups over two columns."""

from typing import Any

from qt.core import QCheckBox, QGroupBox, QHBoxLayout, QLineEdit, QVBoxLayout, QWidget

from ..config_admin import ConfigAdmin
from ..page_defaults import PageDefaults
from .config_page_covers import CoversSection
from .config_page_form import choice_combo, right_form
from .config_page_lanes import LanesSection
from .page_labels import page_width_choices, theme_choices


def _column(*groups: QGroupBox) -> QVBoxLayout:
    """One column of the Page tab: these groups packed at the top."""
    column = QVBoxLayout()
    for group in groups:
        column.addWidget(group)
    column.addStretch()
    return column


class PageTab(QWidget):
    """One library's Page Defaults: the Page, Header, Lanes and Covers groups."""

    def __init__(self, admin: ConfigAdmin, parent: Any = None) -> None:
        super().__init__(parent)
        self.theme = choice_combo(self, theme_choices())
        self.title = QLineEdit(self)
        self.page_width = choice_combo(self, page_width_choices())
        self.show_counts = QCheckBox(_('Show the book and series counts'), self)
        self.show_library = QCheckBox(_('Show the library name'), self)
        self.lanes = LanesSection(self)
        self.covers = CoversSection(self)
        self.unranked = self.lanes.unranked
        self.show_unranked = self.lanes.show_unranked
        layout = QHBoxLayout(self)
        layout.addLayout(_column(self._page_group(), self.lanes))
        layout.addLayout(_column(self._header_group(), self.covers))
        self.load(admin.page_defaults())

    def _page_group(self) -> QGroupBox:
        box = QGroupBox(_('Page'), self)
        form = right_form(box)
        form.addRow(_('Theme'), self.theme)
        form.addRow(_('Title'), self.title)
        form.addRow(_('Page width'), self.page_width)
        return box

    def _header_group(self) -> QGroupBox:
        box = QGroupBox(_('Header'), self)
        form = right_form(box)
        form.addRow(self.show_counts)
        form.addRow(self.show_library)
        return box

    def build_defaults(self) -> PageDefaults:
        """The Page Defaults the widgets currently show."""
        return PageDefaults(
            theme=self.theme.currentData(),
            title=self.title.text(),
            unranked_label=self.unranked.text(),
            show_unranked=self.show_unranked.isChecked(),
            show_counts=self.show_counts.isChecked(),
            show_library=self.show_library.isChecked(),
            page_width=self.page_width.currentData(),
            show_labels=self.lanes.show_labels.isChecked(),
            show_descriptions=self.lanes.show_descriptions.isChecked(),
            lane_gap=self.lanes.lane_gap.currentData(),
            empty_lane=self.lanes.empty_lane.currentData(),
            empty_lane_text=self.lanes.empty_lane_text.text(),
            show_captions=self.covers.show_captions.isChecked(),
            show_read_count=self.covers.show_read_count.isChecked(),
            show_sheets=self.covers.show_sheets.isChecked(),
            cover_size=self.covers.cover_size.currentData(),
            cover_gap=self.covers.cover_gap.currentData(),
        )

    def load(self, defaults: PageDefaults) -> None:
        """Show these Page Defaults."""
        self.theme.setCurrentIndex(max(self.theme.findData(defaults.theme), 0))
        self.title.setText(defaults.title)
        self.page_width.setCurrentIndex(max(self.page_width.findData(defaults.page_width), 0))
        self.show_counts.setChecked(defaults.show_counts)
        self.show_library.setChecked(defaults.show_library)
        self.lanes.load(defaults)
        self.covers.load(defaults)

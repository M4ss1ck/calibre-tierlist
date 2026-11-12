"""The Lanes group of the Page tab: labels, Tier descriptions, the Unranked Lane, Lane Gap and empty Lanes."""

from typing import Any

from qt.core import QCheckBox, QGroupBox, QLineEdit

from ..page_defaults import PageDefaults
from .config_page_form import choice_combo, right_form
from .page_labels import empty_lane_choices, gap_choices


class LanesSection(QGroupBox):
    """The Lane switches, the Unranked Lane label, Lane Gap and the Empty Lane Message."""

    def __init__(self, parent: Any = None) -> None:
        super().__init__(_('Lanes'), parent)
        self.show_labels = QCheckBox(_('Show tier labels'), self)
        self.show_descriptions = QCheckBox(_('Show tier descriptions'), self)
        self.show_unranked = QCheckBox(_('Show the Unranked Lane'), self)
        self.unranked = QLineEdit(self)
        self.lane_gap = choice_combo(self, gap_choices())
        self.empty_lane = choice_combo(self, empty_lane_choices())
        self.empty_lane_text = QLineEdit(self)
        self.empty_lane_text.setPlaceholderText(_('No books in this tier'))
        form = right_form(self)
        form.addRow(self.show_labels)
        form.addRow(self.show_descriptions)
        form.addRow(self.show_unranked)
        form.addRow(_('Unranked Lane label'), self.unranked)
        form.addRow(_('Lane gap'), self.lane_gap)
        form.addRow(_('Empty lane message'), self.empty_lane)
        form.addRow(_('Custom message'), self.empty_lane_text)
        self.empty_lane.currentIndexChanged.connect(self.show_custom_text)

    def load(self, defaults: PageDefaults) -> None:
        """Show these Page Defaults' Lane choices."""
        self.show_labels.setChecked(defaults.show_labels)
        self.show_descriptions.setChecked(defaults.show_descriptions)
        self.show_unranked.setChecked(defaults.show_unranked)
        self.unranked.setText(defaults.unranked_label)
        self.lane_gap.setCurrentIndex(max(self.lane_gap.findData(defaults.lane_gap), 0))
        self.empty_lane.setCurrentIndex(max(self.empty_lane.findData(defaults.empty_lane), 0))
        self.empty_lane_text.setText(defaults.empty_lane_text)
        self.show_custom_text()

    def show_custom_text(self, *_args: object) -> None:
        """Enable the custom Empty Lane Message field only while the Custom message is chosen."""
        self.empty_lane_text.setEnabled(self.empty_lane.currentData() == 'custom')

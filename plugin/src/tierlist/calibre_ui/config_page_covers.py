"""The Covers group of the Page tab: Captions, Read Count, Cover Size and Cover Gap."""

from typing import Any

from qt.core import QCheckBox, QGroupBox

from ..page_defaults import PageDefaults
from .config_page_form import choice_combo, right_form
from .page_labels import cover_size_choices, gap_choices


class CoversSection(QGroupBox):
    """The cover switches, the Cover Size and the Cover Gap."""

    def __init__(self, parent: Any = None) -> None:
        super().__init__(_('Covers'), parent)
        self.show_captions = QCheckBox(_('Show captions'), self)
        self.show_read_count = QCheckBox(_('Show the read count'), self)
        self.cover_size = choice_combo(self, cover_size_choices())
        self.cover_gap = choice_combo(self, gap_choices())
        form = right_form(self)
        form.addRow(self.show_captions)
        form.addRow(self.show_read_count)
        form.addRow(_('Cover size'), self.cover_size)
        form.addRow(_('Cover gap'), self.cover_gap)

    def load(self, defaults: PageDefaults) -> None:
        """Show these Page Defaults' cover choices."""
        self.show_captions.setChecked(defaults.show_captions)
        self.show_read_count.setChecked(defaults.show_read_count)
        self.cover_size.setCurrentIndex(max(self.cover_size.findData(defaults.cover_size), 0))
        self.cover_gap.setCurrentIndex(max(self.cover_gap.findData(defaults.cover_gap), 0))

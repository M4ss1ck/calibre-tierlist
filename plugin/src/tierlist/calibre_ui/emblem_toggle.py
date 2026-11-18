"""The Settings checkbox for cover grid emblems, and calibre's consent prompt for showing them."""

from typing import Any

from calibre.gui2 import gprefs, question_dialog
from qt.core import QCheckBox, QLabel, QVBoxLayout, QWidget

load_translations()


def emblems_hidden(prefs: Any = gprefs) -> bool:
    """Whether calibre's own setting hides cover emblems."""
    if 'emblem_style' in prefs.defaults:
        return prefs['emblem_style'] == 'none'
    return not prefs.get('show_emblems', False)


def show_emblems(prefs: Any = gprefs) -> None:
    """Ask calibre to show cover emblems, leaving their size and position alone."""
    if 'emblem_style' in prefs.defaults:
        prefs['emblem_style'] = 'emboss'
    else:
        prefs['show_emblems'] = True


class EmblemToggle(QWidget):
    """The Show tiers as cover grid emblems checkbox and the note about calibre's own switch."""

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent)
        self.checkbox = QCheckBox(_('Show tiers as cover grid emblems'), self)
        self.note = QLabel(_('Calibre hides cover emblems. Show them in Preferences → Look & feel → Cover grid.'), self)
        self.note.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.note)
        self.checkbox.clicked.connect(self._clicked)
        self._update_note()

    def checked(self) -> bool:
        """Whether cover grid emblems are chosen."""
        return bool(self.checkbox.isChecked())

    def set_checked(self, on: bool) -> None:
        """Show a stored choice without asking calibre anything."""
        self.checkbox.setChecked(on)
        self._update_note()

    def _clicked(self) -> None:
        """On a user tick, offer once to make calibre show the emblems."""
        if self.checked() and emblems_hidden():
            question = _('Calibre hides cover emblems. Show them on the cover?')
            if question_dialog(self, _('Tier List'), question):
                show_emblems()
        self._update_note()

    def _update_note(self) -> None:
        """Show the note only when the choice is on and calibre would hide the emblems."""
        self.note.setVisible(self.checked() and emblems_hidden())

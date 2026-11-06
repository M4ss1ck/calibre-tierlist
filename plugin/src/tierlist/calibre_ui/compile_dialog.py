"""The Compile dialog: pick a Compile Scope and where to write the HTML."""

import os
from typing import Any

from calibre.gui2 import choose_save_file
from qt.core import QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QRadioButton, QVBoxLayout

from ..app import TierList
from ..compile import Scope


class CompileDialog(QDialog):
    """Asks for a Compile Scope and an output path before compiling."""

    def __init__(self, gui: Any, db: Any, app: TierList) -> None:
        super().__init__(gui)
        self.setWindowTitle(_('Compile Tier List'))
        self.library_radio = QRadioButton(_('Whole library'), self)
        self.library_radio.setChecked(True)
        self.virtual_radio = QRadioButton(self._virtual_label(db), self)
        self.virtual_radio.setEnabled(bool(db.data.get_base_restriction_name()))
        self.selection_radio = QRadioButton(_('Current selection'), self)
        self.selection_radio.setEnabled(bool(gui.library_view.get_selected_ids()))
        self.path_edit = QLineEdit(self)
        self.path_edit.setText(app.output_path())
        browse = QPushButton(_('Browse…'), self)
        browse.clicked.connect(self._browse)
        compile_button = QPushButton(_('Compile'), self)
        compile_button.clicked.connect(self.accept)
        cancel_button = QPushButton(_('Cancel'), self)
        cancel_button.clicked.connect(self.reject)
        self._layout(browse, compile_button, cancel_button)

    def accept(self) -> None:
        """Close the dialog only when an output path was given."""
        if not self.path().strip():
            return
        super().accept()

    def scope(self) -> Scope:
        """The Compile Scope the user picked."""
        if self.virtual_radio.isChecked():
            return 'virtual_library'
        if self.selection_radio.isChecked():
            return 'selection'
        return 'library'

    def path(self) -> str:
        """The file the compiled HTML should be written to."""
        return self.path_edit.text()

    def _virtual_label(self, db: Any) -> str:
        name = db.data.get_base_restriction_name()
        if not name:
            return _('Current virtual library')
        return _('Current virtual library (%s)') % name

    def _browse(self) -> None:
        path = choose_save_file(
            self,
            _('Save tier list'),
            _('Save tier list'),
            filters=[(_('HTML files'), ['*.html'])],
            all_files=False,
            initial_path=os.path.dirname(self.path_edit.text()),
            initial_filename=os.path.basename(self.path_edit.text()),
        )
        if path:
            self.path_edit.setText(path)

    def _layout(self, browse: Any, compile_button: Any, cancel_button: Any) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(_('Compile Scope'), self))
        layout.addWidget(self.library_radio)
        layout.addWidget(self.virtual_radio)
        layout.addWidget(self.selection_radio)
        path_row = QHBoxLayout()
        path_row.addWidget(self.path_edit)
        path_row.addWidget(browse)
        layout.addLayout(path_row)
        buttons = QHBoxLayout()
        buttons.addWidget(compile_button)
        buttons.addWidget(cancel_button)
        layout.addLayout(buttons)

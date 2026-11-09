from typing import Any

from tierlist.calibre_ui.config_io import confirm_import as confirm_import
from tierlist.calibre_ui.config_io import export_config as export_config
from tierlist.calibre_ui.config_io import import_config as import_config

# Rebound by itest/config_import.py to stub the file dialog and the message box.
QFileDialog: Any
QMessageBox: Any

"""Importing and exporting Tier Config as JSON from the config dialog."""

from pathlib import Path

from calibre.gui2 import error_dialog
from qt.core import QFileDialog, QMessageBox, QWidget

from ..config_admin import ConfigAdmin
from ..tiers import Tier, TierConfig, TierConfigError, dump_config


def import_config(parent: QWidget, admin: ConfigAdmin) -> TierConfig | None:
    """Ask for a JSON file and return the Tier Config it holds; None on cancel or error."""
    path = QFileDialog.getOpenFileName(parent, _('Import Tier Config'), '', _('JSON files (*.json)'))[0]
    if not path:
        return None
    try:
        return admin.import_json(Path(path).read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, TierConfigError) as exc:
        error_dialog(parent, _('Tier List'), str(exc), show=True)
        return None


def export_config(parent: QWidget, config: TierConfig) -> None:
    """Write this Tier Config to the JSON file the user picks."""
    path = QFileDialog.getSaveFileName(parent, _('Export Tier Config'), 'tier-config.json', _('JSON files (*.json)'))[0]
    if path:
        Path(path).write_text(dump_config(config), encoding='utf-8')


def confirm_import(parent: QWidget, admin: ConfigAdmin, shown: tuple[Tier, ...], incoming: TierConfig) -> bool:
    """True when this import may load, asking first when books hold a Tier it removes."""
    kept = {tier.id for tier in incoming.tiers}
    count = sum(admin.book_count(tier.id) for tier in shown if tier.id not in kept)
    if not count:
        return True
    question = (
        ngettext(
            '%d book holds a Tier this import removes. It will lose its Book Tier and stay read. Import anyway?',
            '%d books hold Tiers this import removes. They will lose their Book Tier and stay read. Import anyway?',
            count,
        )
        % count
    )
    return QMessageBox.question(parent, _('Import Tier Config'), question) == QMessageBox.StandardButton.Yes


def confirm_remove(parent: QWidget, count: int) -> bool:
    """True when a Tier holding `count` books may be removed, asking first when any book holds it."""
    if not count:
        return True
    question = (
        ngettext(
            '%d book holds this Tier. It will lose its Book Tier and stay read. Remove it?',
            '%d books hold this Tier. They will lose their Book Tier and stay read. Remove it?',
            count,
        )
        % count
    )
    return QMessageBox.question(parent, _('Remove Tier'), question) == QMessageBox.StandardButton.Yes

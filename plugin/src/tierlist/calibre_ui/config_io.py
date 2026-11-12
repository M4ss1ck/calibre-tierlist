"""Importing and exporting Settings as JSON from the config dialog."""

from pathlib import Path

from calibre.gui2 import error_dialog
from qt.core import QFileDialog, QMessageBox, QWidget

from ..config_admin import ConfigAdmin
from ..page_defaults import PageDefaults
from ..settings_export import SettingsExport
from ..tiers import Tier, TierConfig, TierConfigError


def import_settings(parent: QWidget, admin: ConfigAdmin) -> SettingsExport | None:
    """Ask for a Settings Export or old Tier Config file and return what it holds; None on cancel or error."""
    path = QFileDialog.getOpenFileName(parent, _('Import Settings'), '', _('JSON files (*.json)'))[0]
    if not path:
        return None
    try:
        return admin.parse_settings_export(Path(path).read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, TierConfigError) as exc:
        error_dialog(parent, _('Tier List'), str(exc), show=True)
        return None


def export_settings(
    parent: QWidget, admin: ConfigAdmin, config: TierConfig, defaults: PageDefaults, include: bool
) -> None:
    """Write these settings to the JSON file the user picks, with Overrides and Lane Order when asked."""
    path = QFileDialog.getSaveFileName(
        parent, _('Export Settings'), 'tierlist-settings.json', _('JSON files (*.json)')
    )[0]
    if path:
        Path(path).write_text(admin.export_settings(config, defaults, include), encoding='utf-8')


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


def confirm_replace(parent: QWidget, export: SettingsExport) -> bool:
    """True when this import may replace existing Overrides and Lane Order, asking first."""
    if export.overrides is None and export.lane_order is None:
        return True
    if export.overrides is None:
        question = _('This replaces the board order. Import anyway?')
    else:
        count = len(export.overrides)
        question = (
            ngettext(
                'This replaces %d series override and the board order. Import anyway?',
                'This replaces %d series overrides and the board order. Import anyway?',
                count,
            )
            % count
        )
    return QMessageBox.question(parent, _('Import Settings'), question) == QMessageBox.StandardButton.Yes


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

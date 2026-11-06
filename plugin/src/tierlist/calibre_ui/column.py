"""First-run offer to create the Tier column, and the creation itself."""

from typing import Any

from calibre.gui2 import error_dialog, info_dialog, question_dialog
from calibre.gui2.preferences.create_custom_column import CreateNewCustomColumn

from ..app import TierList


def offer_tier_column(gui: Any, app: TierList) -> bool:
    """Offer the Tier column once per library, and return True when it was created."""
    if app.tier_column_ready() or app.tier_column_offered():
        return False
    app.mark_tier_column_offered()
    question = _('Create a Tier column so books can be sent to a tier?')
    if question_dialog(gui, _('Tier List'), question) is not True:
        return False
    return create_tier_column(gui, app.tier_config().tier_column)


def create_tier_column(gui: Any, lookup: str) -> bool:
    """Create the Text Tier column, returning True when it was created (usable after a restart)."""
    creator = CreateNewCustomColumn(gui)
    if creator.must_restart():
        info_dialog(gui, _('Tier List'), _('Restart calibre before creating the tier column.'), show=True)
        return False
    result, msg = creator.create_column(lookup, _('Tier'), 'text', False)
    if result is creator.Result.COLUMN_ADDED:
        info_dialog(gui, _('Tier List'), _('Restart calibre before using the tier column.'), show=True)
        return True
    error_dialog(gui, _('Tier List'), msg, show=True)
    return False

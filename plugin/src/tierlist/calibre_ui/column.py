"""First-run offers to create the Tier and Read columns, and the creation itself."""

from typing import Any

from calibre.gui2 import error_dialog, info_dialog, question_dialog
from calibre.gui2.preferences.create_custom_column import CreateNewCustomColumn
from qt.core import QInputDialog

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


def offer_read_column(gui: Any, app: TierList, force: bool = False) -> bool:
    """Offer to track Read State in a date or bool column, returning True when one was created."""
    if not force and (app.read_column_ready() or app.read_column_offered()):
        return False
    if not force and CreateNewCustomColumn(gui).must_restart():
        return False  # another column awaits a restart; offer again on the next start
    app.mark_read_column_offered()
    metadata = gui.current_db.field_metadata
    candidates = {f'{metadata[lookup]["name"]} ({lookup})': lookup for lookup in app.read_column_candidates()}
    new_column = _('A new "Date read" column')
    items = [new_column, *candidates]
    choice, accepted = QInputDialog.getItem(
        gui, _('Tier List'), _('Track the date you read each book in:'), items, 0, False
    )
    if not accepted:
        return False
    if choice == new_column:
        return create_column(gui, app.tier_config().read_column, _('Date read'), 'datetime')
    app.map_read_column(candidates[choice])
    return False


def create_tier_column(gui: Any, lookup: str) -> bool:
    """Create the Text Tier column, returning True when it was created (usable after a restart)."""
    return create_column(gui, lookup, _('Tier'), 'text')


def create_column(gui: Any, lookup: str, heading: str, datatype: str) -> bool:
    """Create a custom column, returning True when it was created (usable after a restart)."""
    creator = CreateNewCustomColumn(gui)
    if creator.must_restart():
        info_dialog(gui, _('Tier List'), _('Restart calibre before creating the new column.'), show=True)
        return False
    result, msg = creator.create_column(lookup, heading, datatype, False)
    if result is creator.Result.COLUMN_ADDED:
        info_dialog(gui, _('Tier List'), _('Restart calibre before using the new column.'), show=True)
        return True
    error_dialog(gui, _('Tier List'), msg, show=True)
    return False

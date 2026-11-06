# SLICE: calibre_ui

## Purpose

Adapts the calibre-free core to calibre's GUI: it registers the Tier List action, sends books to a Tier, and offers to create the Tier column. It is separate so the core stays importable, and testable, without calibre or Qt.

## Public API

- `TierListAction`: the `InterfaceAction` that calibre instantiates through the zip root entry point.
- `tier_list(db) -> TierList`: the facade over one calibre library database and its namespaced prefs.
- `CalibreLibrary`, `CalibrePrefs`: the `Library` and `Prefs` port adapters.
- `TierMenu(action)`: the "Send to tier" submenu, rebuilt on demand.
- `offer_tier_column(gui, app) -> bool`: the first-run offer, and whether a column was created.
- `create_tier_column(gui, lookup) -> bool`: creates the Text Tier column; True means restart calibre.

## Files

- `action.py`: the action, its toolbar dialog, the layout claim, and the send/clear handlers.
- `adapters.py`: `CalibreLibrary` and `CalibrePrefs` over calibre's database.
- `menu.py`: the `TierMenu` submenu and its shortcut registration.
- `column.py`: the first-run offer and the tier column creation flow.

## Depends on

- Ports: `Library` and `Prefs`, implemented here by `CalibreLibrary` and `CalibrePrefs`.
- Slices: `tierlist.app` and `tierlist.tiers` for the use cases and Tier Config.
- Imports calibre and Qt; the only slice allowed to.

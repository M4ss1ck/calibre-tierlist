# SLICE: calibre_ui

## Purpose

Adapts the calibre-free core to calibre's GUI: it registers the Tier List action, sends books to a Tier, marks books read or unread, and offers to create the Tier and Read columns. It is separate so the core stays importable, and testable, without calibre or Qt.

## Public API

- `TierListAction`: the `InterfaceAction` that calibre instantiates through the zip root entry point.
- `tier_list(db) -> TierList`: the facade over one calibre library database and its namespaced prefs.
- `CalibreLibrary`, `CalibrePrefs`: the `Library` and `Prefs` port adapters.
- `TierMenu(action)`: the "Send to tier" submenu and the Read State menu items, rebuilt on demand.
- `offer_tier_column(gui, app) -> bool`: the first-run Tier offer, and whether a column was created.
- `offer_read_column(gui, app, force=False) -> bool`: the Read State offer (new "Date read" column or an existing date/bool column), and whether a column was created.
- `create_column(gui, lookup, heading, datatype) -> bool`: creates any custom column; True means restart calibre.
- `create_tier_column(gui, lookup) -> bool`: creates the Text Tier column; True means restart calibre.
- `CompileDialog(gui, db, app)`: the Compile dialog; `scope()` returns `'library'`, `'virtual_library'`, or `'selection'`, and `path()` the output file.
- `scope_book_ids(gui, scope) -> tuple[int, ...]`: the sorted book ids a Compile Scope covers.
- `run_compile(app, request, template, path, log) -> str`: compiles to a file through the facade; shared by the job and the integration test.
- `start_compile(action, request, template, path)`: runs `run_compile` in a calibre background job, then opens the HTML.

## Files

- `action.py`: the action, its toolbar dialog, the layout claim, and the send, clear, and mark read/unread handlers.
- `adapters.py`: `CalibreLibrary` (including date conversion) and `CalibrePrefs` over calibre's database.
- `menu.py`: the `TierMenu` submenu, Read State items, and their shortcut registration.
- `column.py`: the first-run offers and the column creation flow.
- `compile_dialog.py`: the Compile Scope and output path dialog.
- `compile_job.py`: Compile Scope book ids, the background job, and opening the written file.

## Depends on

- Ports: `Library` and `Prefs`, implemented here by `CalibreLibrary` and `CalibrePrefs`.
- Slices: `tierlist.app` and `tierlist.tiers` for the use cases and Tier Config.
- Imports calibre and Qt; the only slice allowed to.

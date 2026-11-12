# SLICE: calibre_ui

## Purpose

Adapts the calibre-free core to calibre's GUI: it registers the Tier List action, sends books to a Tier, marks books read or unread, offers to create the Tier and Read columns, and hosts the Settings dialog, which opens from the Tier List menu and from calibre's Preferences > Plugins. It is separate so the core stays importable, and testable, without calibre or Qt.

## Public API

- `TierListAction`: the `InterfaceAction` that calibre instantiates through the zip root entry point.
- `tier_list(db) -> TierList`: the facade over one calibre library database and its namespaced prefs.
- `config_admin(db) -> ConfigAdmin`: the config-dialog use cases over one calibre library database.
- `CalibreLibrary`, `CalibrePrefs`: the `Library` and `Prefs` port adapters.
- `CalibreSavedSearches`: the `SavedSearches` port adapter over calibre's saved searches.
- `CalibreCovers`: the `Covers` port adapter, encoding cover thumbnails as AVIF, WebP, or JPEG.
- `TierMenu(action)`: the "Send to tier" and "Set series tier" submenus, the Read State menu items, and closing "Arrange board…" and "Settings…" items, rebuilt on demand; each Tier item carries a swatch of its colour.
- `plugin_icon(plugin_name)`: the plugin's toolbar and context menu icon, `images/icon.png` in the zip, read through calibre's `get_icons`.
- `tier_swatch(colour) -> QIcon`: a square of a Tier's colour for menu items.
- `offer_tier_column(gui, app) -> bool`: the first-run Tier offer, and whether a column was created.
- `offer_read_column(gui, app, force=False) -> bool`: the Read State offer (new "Date read" column or an existing date/bool column), and whether a column was created.
- `create_column(gui, lookup, heading, datatype) -> bool`: creates any custom column; True means restart calibre.
- `create_tier_column(gui, lookup) -> bool`: creates the Text Tier column; True means restart calibre.
- `CompileDialog(gui, db, app)`: the Compile dialog; `scope()` returns `'library'`, `'virtual_library'`, or `'selection'`, and `path()` the output file.
- `ConfigWidget(gui)`: the tabbed Settings widget calibre shows under Customize and the Settings dialog hosts; its `tiers`, `page`, `arrange` and `export` tabs hold the widgets; `build_config()` reads the Tier Config they show, `validate()` returns False after showing why an invalid one cannot be saved, `select(name)` shows one tab by attribute name, and `save()` stores the Tier Config and Page Defaults, writes the staged Arrange drops and an imported Settings Export's Overrides and Lane Order, and refreshes saved searches and the Tier menu.
- `SettingsDialog(gui, parent=None, tab=None)`: the Settings dialog, OK and Cancel; `tab` opens on a named tab (`'arrange'` from the menu), `accept()` validates then saves, and Cancel writes nothing.
- `TiersTab(admin, parent)`: the Tier table, its buttons, the column mapping and the Orphaned Overrides; `build_config()` reads them, `load()` and `load_tiers()` show them.
- `PageTab(admin, parent)`: the Page Defaults in four groups — Page (theme, title, Page Width), Header (counts and library name), Lanes (labels, Tier descriptions, Unranked Lane, Lane Gap, Empty Lane Message) and Covers (Captions, Read Count, Cover Size, Cover Gap); `build_defaults()` reads them and `load(defaults)` shows them.
- `ArrangeTab(gui, parent)`: the whole-library board as wrapping Lane rows of covers; `drop(kind, key, target, index)` stages one drag and `save()` writes the staged drops. Covers load off the GUI thread once the tab is shown.
- `LaneList(lane_tier, on_drop, parent)`: one Lane's wrapping duplicate of the board; it translates a drop into its handler and never writes.
- `ExportTab(admin, tiers, page, parent)`: the Import JSON… and Export JSON… buttons and the "Include series Overrides and Lane Order" checkbox; an import accepts a Settings Export or an old Tier Config, asks first when it drops Tiers books still hold or replaces stored Overrides/Lane Order, loads its sections into the tabs, and writes its Overrides and Lane Order when Settings saves.
- `TierTable(parent)`: the Tier rows; `tiers()` and `set_tiers()` convert to and from `Tier`s, `add()`, `remove(row)`, and `move(row, offset)` edit them.
- `OrphanPanel(admin, series_names, parent)`: the Orphaned Overrides list, reattaching and deleting immediately.
- `scope_book_ids(gui, scope) -> tuple[int, ...]`: the sorted book ids a Compile Scope covers.
- `run_compile(app, request, template, path, log) -> str`: compiles to a file through the facade; shared by the job and the integration test.
- `start_compile(action, request, template, path)`: runs `run_compile` in a calibre background job, then opens the HTML.

## Files

- `action.py`: the action and its icon, its toolbar dialog, its Settings and Arrange dialog openers, the layout claim, and the send, clear, and mark read/unread handlers.
- `adapters.py`: `CalibreLibrary` (including date conversion), `CalibrePrefs`, and `CalibreSavedSearches` over calibre's database, plus the `tier_list` and `config_admin` factories.
- `covers.py`: `CalibreCovers`, the cover thumbnails and their dominant colour.
- `icons.py`: the plugin icon and the Tier colour swatches.
- `menu.py`: the `TierMenu` submenus, Read State items, the Arrange board and Settings items, and their shortcut registration.
- `series_menu.py`: the Set series tier submenu's Override and Auto items.
- `column.py`: the first-run offers and the column creation flow.
- `compile_dialog.py`: the Compile Scope and output path dialog.
- `compile_job.py`: Compile Scope book ids, the background job, and opening the written file.
- `config_widget.py`: the tabbed Settings widget: its tabs and the validating save.
- `settings_dialog.py`: the Settings dialog the Tier List menu opens, with OK and Cancel.
- `config_tiers.py`: the Tiers tab: the Tier table, the column mapping, and the Orphaned Overrides.
- `config_page.py`: the Page tab: the Page and Header groups, and the Page Defaults the tab reads and shows.
- `config_page_lanes.py`: the Lanes group: labels, Tier descriptions, the Unranked Lane, Lane Gap and the Empty Lane Message.
- `config_page_covers.py`: the Covers group: Captions, Read Count, Cover Size and Cover Gap.
- `config_page_form.py`: the right-aligned form and the contract-value combos the Page tab's groups share.
- `config_arrange.py`: the Arrange tab: the Lane rows, the staged board, and saving its drops.
- `arrange_lane.py`: one Lane's wrapping cover list, the drop-to-handler bridge, and the off-thread thumbnail loader.
- `config_export.py`: the Export tab: importing and exporting Settings JSON, with the Overrides and Lane Order opt-in.
- `tier_table.py`: the Tier table rows and their colour swatch button.
- `config_extras.py`: the column mapping combos and the Orphaned Overrides panel.
- `config_form.py`: the button row and mapping form layout pieces.
- `config_io.py`: importing and exporting Settings JSON, and the import and Tier removal confirmations.

## Depends on

- Ports: `Library`, `Prefs`, `SavedSearches`, and `Covers`, implemented here by `CalibreLibrary`, `CalibrePrefs`, `CalibreSavedSearches`, and `CalibreCovers`.
- Slices: `tierlist.app`, `tierlist.config_admin`, `tierlist.page_defaults` for Page Defaults, `tierlist.arrange` for the staged board and its drops, `tierlist.settings_export` for the export file, and `tierlist.tiers` for the use cases and Tier Config.
- Imports calibre and Qt; the only slice allowed to.

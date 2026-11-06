# SLICE: compile

## Purpose

Turns the books the library holds into Tier List Data: the versioned payload the compiled board is drawn from. It is separate so the facade reads ports while filtering, ordering, and the JSON shape stay calibre-free and testable.

## Public API

- `Generated(at, library_name, scope, plugin_version)`: when, where, and for which Compile Scope a compile ran.
- `CompileRequest(scope, book_ids, library_name, plugin_version)`: the inputs one compile needs.
- `Book(id, title, tier, date_read)`: one book on the board.
- `Lane(tier, cards)`: one row of the board, its Tier id or None for the Unranked Lane, and its ordered book ids.
- `TierListData(generated, tiers, lanes, books)`: the whole board; `to_dict()` returns the schema's camelCase JSON shape.
- `READ_COLUMN_TYPES`: the calibre column datatypes that can hold Read State.
- `compile_data(generated, library, config, book_ids) -> TierListData`: reads title, Book Tier, and Read State through the Library port and builds the board.

## Files

- `data.py`: the frozen data types and their JSON serialisation.
- `build.py`: filters read books, resolves Book Tiers, orders Lanes, and reads the ports.

## Depends on

- Ports: `Library` for titles, Book Tier, Read State, and column readiness.
- Slices: `tiers` for `Tier` and `TierConfig`.
- Imports nothing from calibre or Qt.

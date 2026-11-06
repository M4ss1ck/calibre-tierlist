# SLICE: compile

## Purpose

Turns the books the library holds into Tier List Data: the versioned payload the compiled board is drawn from. It is separate so the facade reads ports while filtering, ordering, and the JSON shape stay calibre-free and testable.

## Public API

- `Generated(at, library_name, scope, plugin_version)`: when, where, and for which Compile Scope a compile ran.
- `CompileRequest(scope, book_ids, library_name, plugin_version)`: the inputs one compile needs.
- `Book(id, title, tier, date_read)`: one book on the board.
- `Lane(tier, cards)`: one row of the board, its Tier id or None for the Unranked Lane, and its ordered book ids.
- `TierListData(generated, tiers, lanes, books, covers)`: the whole board; `covers` maps book id to `Cover` for books that have one, and `to_dict()` returns the schema's camelCase JSON shape.
- `Cover(format, data, colour)`: one book's cover thumbnail bytes, their image format, and its dominant colour.
- `COVER_WIDTH`: the pixel width every embedded cover thumbnail is rendered at.
- `choose_format(available) -> str`: the first preferred cover format the host encodes, or JPEG.
- `READ_COLUMN_TYPES`: the calibre column datatypes that can hold Read State.
- `compile_data(generated, library, covers, fmt, config, book_ids) -> TierListData`: reads title, Book Tier, and Read State through the Library port, builds the board, then reads a `fmt` cover at `COVER_WIDTH` for each book on it.

## Files

- `data.py`: the frozen data types and their JSON serialisation.
- `build.py`: filters read books, resolves Book Tiers, orders Lanes, and reads the ports.
- `covers.py`: the `Cover` type, its thumbnail width, and the format preference order.

## Depends on

- Ports: `Library` for titles, Book Tier, Read State, and column readiness; `Covers` for cover thumbnails.
- Slices: `tiers` for `Tier` and `TierConfig`.
- Imports nothing from calibre or Qt.

# SLICE: compile

## Purpose

Turns the books the library holds into Tier List Data: the versioned payload the compiled board is drawn from. It is separate so the facade reads ports while filtering, ordering, and the JSON shape stay calibre-free and testable.

## Public API

- `Generated(at, library_name, scope, plugin_version)`: when, where, and for which Compile Scope a compile ran.
- `CompileRequest(scope, book_ids, library_name, plugin_version)`: the inputs one compile needs.
- `Book(id, title, tier, date_read, read, details)`: one book on the board; `read` is its resolved Read State.
- `Details(authors, series, series_index, rating, tags, blurb)`: what the detail panel shows; `rating` is stars out of 5 in half steps, None when unrated.
- `blurb(comments) -> str | None`: calibre's HTML comments as plain text (no script or style contents, entities unescaped, whitespace collapsed), trimmed at a word boundary near `BLURB_LIMIT` (600) with an ellipsis.
- `Lane(tier, items)`: one row of the board, its Tier id or None for the Unranked Lane, and its ordered `LaneItem`s.
- `LaneItem(stack, card)`: one item in a Lane, a Stack by series name or a Card by book id; exactly one is set.
- `Series(colour, positions, override)`: one series on the board, the colour its Placeholders are drawn in, every position (the Series Panel lists them all), and whether its Series Tier is an Override.
- `Position(number, book)`: one Stack position, the series index as displayed, and the owned book id or None for a Placeholder.
- `TierListData(generated, tiers, lanes, books, covers, series)`: the whole board; `books` holds every book on it, `series` maps series name to `Series`, `covers` maps book id to `Cover` for books that have one, and `to_dict()` returns the schema's camelCase JSON shape.
- `Cover(format, data, colour)`: one book's cover thumbnail bytes, their image format, and its dominant colour.
- `COVER_WIDTH`: the pixel width every embedded cover thumbnail is rendered at.
- `choose_format(available) -> str`: the first preferred cover format the host encodes, or JPEG.
- `cover_thumbs(covers, book_ids, fmt, width) -> dict[int, Cover]`: the thumbnails these books have, by id, encoded on a small pool (a pool, because the host's codec dominates a compile and releases the GIL); a host that cannot encode raises as it would have walked in order.
- `dominant_colour(pixels) -> str`: the most common colour of these RGB pixels, or grey when there are none.
- `READ_COLUMN_TYPES`: the calibre column datatypes that can hold Read State.
- `compile_data(generated, library, covers, fmt, config, book_ids, overrides, order=None) -> TierListData`: reads title, authors, series, series index, Series total, rating, tags, comments, Book Tier, and Read State through the Library port, builds the board, then reads a `fmt` cover at `COVER_WIDTH` for each book on it. `overrides` maps a series name to its Override Tier id; an applicable Override also puts an otherwise unread, untiered series on the board. `order` maps a Lane key (a Tier id or `unranked`) to its stored Lane Order places: they come first in stored order, then every unplaced Stack and Card by date read, undated last, then name or title, then id.
- `count_series(library, book_ids) -> int`: the number of distinct non-empty series among these books.

## Files

- `data.py`: the frozen data types and their JSON serialisation.
- `build.py`: decides which books are on the board, resolves Book Tiers and Series Tiers, orders each Lane's Stacks and Cards, and reads the ports.
- `rows.py`: one library row, the rule for which rows belong on the board, and its Details.
- `blurb.py`: the HTML-to-plain-text blurb sanitiser.
- `series.py`: Series Stacks, their positions, Placeholders, Lane Order, and the Series Tier rule.
- `covers.py`: the thumbnail width, the format preference order, the thumbnail pool, and the dominant colour.

## Depends on

- Ports: `Library` for titles, series, series index, Book Tier, Read State, and column readiness; `Covers` for cover thumbnails.
- Slices: `tiers` for `Tier` and `TierConfig`; `lane_order` for the `Place` a stored Lane Order holds.
- Imports nothing from calibre or Qt.

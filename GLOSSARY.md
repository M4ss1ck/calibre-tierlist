# Glossary

Vocabulary for the Tier List calibre plugin. One context, one glossary. Slice briefs (`SLICE.md`) point here instead of redefining terms.

## Ranking

**Tier**
A user-defined rank with a stable id, label, colour, optional description, and position. Defaults are S, A, B, C, D, F with conventional colours.
Avoid: rank, grade, bucket, category.

**Tier Config**
The ordered list of Tiers for one library, plus plugin settings (column mapping, stack depth). Stored in per-library prefs and importable/exportable as JSON.
Avoid: tier scheme, tier list (that is the compiled board).

**Book Tier**
The Tier id stored on a book in a Text custom column. Setting one also marks the book read.
Avoid: tier label, tier name.

**Read State**
Whether a book is read, and when. Held in a Date column (date read) or a mapped Yes/No column.
Avoid: read flag, status.

**Series Tier**
The Tier a series is shown in. Either an Override or Auto (resolved from the series' books).
Avoid: series rank, series placement.

**Override**
A Series Tier set explicitly for a series by name. It wins over the computed tier and applies to every book in the series, including books added later.
Avoid: manual tier, pinned tier.

**Auto**
A Series Tier with no Override: the most common Book Tier among the series' tiered books, ties going to the lower Tier.
Avoid: default, fallback.

**Orphaned Override**
An Override whose series name matches no series in the library, usually after a series rename. The config UI lists these so they can be reattached or deleted.

## Board

**Stack**
The visual group for one series inside a Tier row: a single front cover (the first owned book with a cover, else the series colour) with up to two sheets peeking out behind it, an "owned/total" count and the series name. Clicking it opens the Series Panel, which lists every position.
Avoid: pile, deck.

**Card**
The visual unit for a standalone book, shown on its own in its Tier.
Avoid: tile, chip.

**Placeholder**
A series position the user does not own. The Series Panel lists it as "Not in your library" and it opens the Detail Panel like an owned position; a Stack with no owned cover is drawn in the series colour (the dominant cover colour of its first covered book in index order). An owned book without a cover uses the Placeholder style with a "no cover" mark on its Card.
Avoid: ghost cover, missing book (that is the position, not the drawing).

**Stack Depth**
A Tier Config setting, 0 to 6, default 3, that the payload still carries as each series' `more` count. It no longer drives the board: a Stack always shows one front cover and the Series Panel lists every position.
Avoid: stack size, fan count.

**Series Panel**
The dialog a Stack opens: the series name, how many of its books are in the library, and one row per position in index order, each owned book with its Book Tier and each Placeholder as "Not in your library". Picking a row opens the Detail Panel.
Avoid: expanded Stack, series popup.

**Sheet**
Everything the reader keeps of the page: the title, the Lanes and the footer. The title and each Lane's label can be renamed in place on the page (not saved); the PNG export draws the Sheet without its controls and filters.
Avoid: canvas, page (that is the whole HTML file).

**Series Total**
The number of books a series has, read from an optional Integer column. When set, every missing whole position up to it becomes a Placeholder; otherwise only gaps up to the highest owned whole index do.
Avoid: series length, series count.

**Lane**
A row on the board. Each Tier is a Lane, plus the Unranked Lane.
Avoid: row, section, column.

**Unranked Lane**
The Lane at the bottom of the board holding read books with no Book Tier. An "Unranked lane" switch shows or hides it on the page; it is shown by default and not saved.
Avoid: unread lane, read lane.

**Detail Panel**
The dialog that opens from a Card or a Series Panel row, showing everything known about that book (or, for a Placeholder, its series, number and that it is not in the library). A book with no Book Tier shows "Unranked".
Avoid: modal, popup, info box.

**Blurb**
A book's description, calibre's HTML comments sanitised to plain text and trimmed at a word boundary, shown in the Detail Panel.
Avoid: summary, synopsis.

**Board Filter**
The search text plus the author, tag and year-read criteria that hide Cards and Stacks on the compiled page. It is set on the page and not saved; Compile Scope is what decides which books the page holds.
Avoid: compile scope, library filter.

## Compile

**Compile Scope**
Which books a compile reads: whole library, current virtual library, or current selection.
Avoid: filter, query, source.

**Tier List Data**
The versioned, schema-defined payload the plugin embeds in the HTML: schema version, generation metadata, Tiers, Lanes, books, series, and covers. Defined by `contract/tierlist.schema.json`.
Avoid: payload, export data, JSON blob.

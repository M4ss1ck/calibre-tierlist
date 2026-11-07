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
The visual group for one series inside a Tier row. It lists the series positions in index order, index 1 in front, with up to Stack Depth more fanned behind and the rest counted as "+N".
Avoid: pile, deck.

**Card**
The visual unit for a standalone book, shown on its own in its Tier.
Avoid: tile, chip.

**Placeholder**
A simulated cover for a series position the user does not own, drawn in the series colour (the dominant cover colour of its first covered book in index order) with the series name and number. An owned book without a cover uses the Placeholder style with a "no cover" mark.
Avoid: ghost cover, missing book (that is the position, not the drawing).

**Stack Depth**
How many positions a Stack shows behind its front, 0 to 6, default 3. Part of Tier Config.
Avoid: stack size, fan count.

**Series Total**
The number of books a series has, read from an optional Integer column. When set, every missing whole position up to it becomes a Placeholder; otherwise only gaps up to the highest owned whole index do.
Avoid: series length, series count.

**Lane**
A row on the board. Each Tier is a Lane, plus the Unranked Lane.
Avoid: row, section, column.

**Unranked Lane**
The Lane at the bottom of the board holding read books with no Book Tier. It can be toggled off on the page.
Avoid: unread lane, read lane.

## Compile

**Compile Scope**
Which books a compile reads: whole library, current virtual library, or current selection.
Avoid: filter, query, source.

**Tier List Data**
The versioned, schema-defined payload the plugin embeds in the HTML: schema version, generation metadata, Tiers, Lanes, books, series, and covers. Defined by `contract/tierlist.schema.json`.
Avoid: payload, export data, JSON blob.

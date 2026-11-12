# Glossary

Vocabulary for the Tier List calibre plugin. One context, one glossary. Slice briefs (`SLICE.md`) point here instead of redefining terms.

## Ranking

**Tier**
A user-defined rank with a stable id, label, colour, optional description, and position. Defaults are S, A, B, C, D, F with conventional colours.
Avoid: rank, grade, bucket, category.

**Tier Config**
The ordered list of Tiers for one library, plus plugin settings (column mapping). Stored in per-library prefs and carried between libraries by a Settings Export.
Avoid: tier scheme, tier list (that is the compiled board).

**Settings**
The one dialog that edits everything the plugin keeps per library: Tier Config, Page Defaults, Lane Order (through the Arrange View) and Settings Export. It opens from the Tier List toolbar menu and from calibre's plugin preferences.
Avoid: config dialog, preferences, options.

**Settings Export**
A JSON file holding a library's Tier Config and Page Defaults, plus its Overrides and Lane Order when the reader opts in. Importing one replaces those settings in another library.
Avoid: backup (Book Tiers and Read State stay in columns and are not in it), config export.

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
A Series Tier set explicitly for a series by name, from the book list menu or by dragging the series to another Lane in the Arrange View. It wins over the computed tier and applies to every book in the series, including books added later.
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

**Series Panel**
The dialog a Stack opens: the series name, how many of its books are in the library, and one row per position in index order, each owned book with its Book Tier and each Placeholder as "Not in your library". Picking a row opens the Detail Panel.
Avoid: expanded Stack, series popup.

**Sheet**
Everything the reader keeps of the page: the title, the Lanes and the footer. The title and each Lane's label start from Page Defaults and Tier labels and can be renamed in place on the page (not saved); the PNG export draws the Sheet without its controls and filters.
Avoid: canvas, page (that is the whole HTML file).

**Series Total**
The number of books a series has, read from an optional Integer column. When set, every missing whole position up to it becomes a Placeholder; otherwise only gaps up to the highest owned whole index do.
Avoid: series length, series count.

**Lane**
A row on the board. Each Tier is a Lane, plus the Unranked Lane.
Avoid: row, section, column.

**Lane Order**
The reader's hand-set order of the Stacks and Cards inside each Lane, kept per library. A Stack or Card with no place yet (a new series, a book newly tiered, or a series Auto moved to another Tier) goes at the end of its Lane; several at once go earliest date read first, then by name. A renamed series loses its place.
Avoid: sort, stack order, ranking.

**Arrange View**
The part of Settings that shows the board as Lanes of covers so the reader can drag. Dragging within a Lane sets Lane Order; dragging a series to another Tier's Lane sets its Override, and to the Unranked Lane clears it; dragging a standalone book to another Lane sets or clears its Book Tier.
Avoid: board editor, sorter, drag mode.

**Page Defaults**
The choices a compiled page opens with, set in Settings and written into the page: theme, Sheet title, Unranked Lane label and whether it is shown, and whether the header shows the counts and library name. A query in the page's address can override any of them for that one opening; changes made on the page are never saved.
Avoid: page settings, view options, preferences.

**Unranked Lane**
The Lane at the bottom of the board holding read books with no Book Tier. An "Unranked lane" switch shows or hides it on the page; whether it starts shown, and its label, are Page Defaults, and the switch is not saved.
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

# SLICE: board

## Purpose

Draws the compiled Tier List as Lanes of Stacks and Cards: one Lane per Tier in config order, then the Unranked Lane. It is separate so rendering stays a pure function of Tier List Data.

## Public API

- `App(data)`: the whole board, one `Lane` per Lane in Tier List Data, an `aria-pressed` toggle that hides or shows the Unranked Lane (shown by default, not persisted), an `aria-pressed` "Dark theme" toggle that pins the `theme` slice's light or dark theme for the session (dark when the system asks for it), the `FilterBar` whose `Filters` it holds, the `export` slice's "Export PNG" control wired to the Lanes wrapper, plus the detail panel for whatever was last opened. Every colour comes from the `theme` tokens; the header and each Lane fold onto one or two lines on a phone.
- `Lane(lane, tiers, books, covers, series, filters, onopen)`: one Lane, with its label and colour from its Tier, its Stacks before its Cards; each Stack is looked up in `series`, each Card resolves its cover from `covers`. Its root carries `data-lane-id`: the Tier id, or `unranked`. Only Cards whose book `matchesBook` and Stacks whose series `matchesSeries` (over the series' books) are drawn; the Lane itself stays even when empty.
- `Stack(name, series, books, covers, tiers, onopen)`: one series' positions, collapsed to all but the `more` it cuts, front first and the rest fanned behind, with its `more` badge and a Tier badge per shown owned position; an `aria-expanded` toggle (when it has more than one position) lays out every position side by side and collapses it again.
- `Position(name, number, book, cover, background, layer, onopen)`: one Stack position as a button that opens the detail panel.
- `Card(title, cover, onopen)`: one book's title as a Card; `cover` is its Cover or undefined for the Placeholder style.
- `Detail(selection, tiers, onclose)`: the detail panel, a modal `<dialog>` for a `Selection` (a `Book`, or a Placeholder's series and number); `onopen` callbacks pass one up.

## Files

- `Card.svelte`: one book's cover with its title caption, or the Placeholder style when it has no cover; a button that opens the detail panel.
- `Detail.svelte`: the detail panel; shows only the fields a book has, closes on Escape or its close button, and the browser returns focus to the opener.
- `Stack.svelte`: one Stack; collapses or expands its positions, labels shown owned positions with their Book Tier, and marks an Override Series Tier with an Override badge (top corner) plus `data-override="true"`.
- `Position.svelte`: one Stack position; dims unread books and draws the Placeholder style for positions with no book or no cover.
- `OverrideMark.svelte`: the Override badge.
- `Lane.svelte`: one Lane; resolves its Tier, skips card and series names missing from Tier List Data, applies the `Filters` to its Cards and Stacks, passes each book's cover, and exposes its id as `data-lane-id` for the export slice.

## Depends on

- Ports: none; it draws the Tier List Data passed as props.
- Slices: `contract` for `TierListData`, `Tier`, `Lane`, `Book`, `Series`, `Position`, and `Cover` types; `filter` for the `Filters` type and its predicates (App also mounts `FilterBar`); `theme` for the colour tokens and the header toggle's system lookup; `export` for the `ExportButton` App places in the header (the export slice reads the Lanes back through `data-lane-id`).
- Svelte only; no calibre or network access.

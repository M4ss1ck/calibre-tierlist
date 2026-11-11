# SLICE: board

## Purpose

Draws the compiled Tier List as Lanes of Stacks and Cards: one Lane per Tier in config order, then the Unranked Lane. It is separate so rendering stays a pure function of Tier List Data.

## Public API

- `App(data)`: the whole board, one `Lane` per Lane in Tier List Data, plus the detail panel for whatever was last opened.
- `Lane(lane, tiers, books, covers, series, onopen)`: one Lane, with its label and colour from its Tier, its Stacks before its Cards; each Stack is looked up in `series`, each Card resolves its cover from `covers`.
- `Stack(name, series, books, covers, tiers, onopen)`: one series' positions, front first and the rest fanned behind, with its `more` badge and a Tier badge per owned position.
- `Card(title, cover, onopen)`: one book's title as a Card; `cover` is its Cover or undefined for the Placeholder style.
- `Detail(selection, tiers, onclose)`: the detail panel, a modal `<dialog>` for a `Selection` (a `Book`, or a Placeholder's series and number); `onopen` callbacks pass one up.

## Files

- `Card.svelte`: one book's cover with its title caption, or the Placeholder style when it has no cover; a button that opens the detail panel.
- `Detail.svelte`: the detail panel; shows only the fields a book has, closes on Escape or its close button, and the browser returns focus to the opener.
- `Stack.svelte`: one Stack; draws each position as a button that opens the detail panel, dims unread books, draws the Placeholder style for positions with no book or no cover, labels owned positions with their Book Tier, and marks an Override Series Tier with an Override badge (top corner) plus `data-override="true"`.
- `Lane.svelte`: one Lane; resolves its Tier, skips card and series names missing from Tier List Data, and passes each book's cover.

## Depends on

- Ports: none; it draws the Tier List Data passed as props.
- Slices: `contract` for `TierListData`, `Tier`, `Lane`, `Book`, `Series`, `Position`, and `Cover` types.
- Svelte only; no calibre or network access.

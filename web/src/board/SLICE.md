# SLICE: board

## Purpose

Draws the compiled Tier List as Lanes of Stacks and Cards: one Lane per Tier in config order, then the Unranked Lane. It is separate so rendering stays a pure function of Tier List Data.

## Public API

- `App(data)`: the whole board, one `Lane` per Lane in Tier List Data.
- `Lane(lane, tiers, books, covers, series)`: one Lane, with its label and colour from its Tier, its Stacks before its Cards; each Stack is looked up in `series`, each Card resolves its cover from `covers`.
- `Stack(name, series, books, covers, tiers)`: one series' positions, front first and the rest fanned behind, with its `more` badge and a Tier badge per owned position.
- `Card(title, cover)`: one book's title as a Card; `cover` is its Cover or undefined for the Placeholder style.

## Files

- `Card.svelte`: one book's cover with its title caption, or the Placeholder style when it has no cover.
- `Stack.svelte`: one Stack; draws each position, dims unread books, draws the Placeholder style for positions with no book or no cover, and labels owned positions with their Book Tier.
- `Lane.svelte`: one Lane; resolves its Tier, skips card and series names missing from Tier List Data, and passes each book's cover.

## Depends on

- Ports: none; it draws the Tier List Data passed as props.
- Slices: `contract` for `TierListData`, `Tier`, `Lane`, `Book`, `Series`, `Position`, and `Cover` types.
- Svelte only; no calibre or network access.

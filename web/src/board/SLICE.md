# SLICE: board

## Purpose

Draws the compiled Tier List as Lanes of Cards: one Lane per Tier in config order, then the Unranked Lane. It is separate so rendering stays a pure function of Tier List Data.

## Public API

- `App(data)`: the whole board, one `Lane` per Lane in Tier List Data.
- `Lane(lane, tiers, books, covers)`: one Lane, with its label and colour from its Tier and its Cards in order; each Card resolves its cover from `covers`.
- `Card(title, cover)`: one book's title as a Card; `cover` is its Cover or undefined for the Placeholder style.

## Files

- `Card.svelte`: one book's cover with its title caption, or the Placeholder style when it has no cover.
- `Lane.svelte`: one Lane; resolves its Tier, skips card ids missing from the books, and passes each book's cover.

## Depends on

- Ports: none; it draws the Tier List Data passed as props.
- Slices: `contract` for `TierListData`, `Tier`, `Lane`, and `Book` types.
- Svelte only; no calibre or network access.

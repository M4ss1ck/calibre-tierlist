# SLICE: board

## Purpose

Draws the compiled Tier List as Lanes of Cards: one Lane per Tier in config order, then the Unranked Lane. It is separate so rendering stays a pure function of Tier List Data.

## Public API

- `App(data)`: the whole board, one `Lane` per Lane in Tier List Data.
- `Lane(lane, tiers, books)`: one Lane, with its label and colour from its Tier and its Cards in order.
- `Card(title)`: one book's title as a Card.

## Files

- `Card.svelte`: one book's title as a Card.
- `Lane.svelte`: one Lane; resolves its Tier and skips card ids missing from the books.

## Depends on

- Ports: none; it draws the Tier List Data passed as props.
- Slices: `contract` for `TierListData`, `Tier`, `Lane`, and `Book` types.
- Svelte only; no calibre or network access.

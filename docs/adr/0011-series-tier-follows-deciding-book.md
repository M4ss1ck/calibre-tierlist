# 0011 Series Tier follows its Deciding Book

Status: Accepted
Date: 2026-11-23
Supersedes: the Override part of ADR 0002; the cross-Lane drags of ADR 0010

## Context

A Series Tier was either an Override, kept in per-library prefs by series name, or Auto, the most common Book Tier among the series' books. That meant two sources of truth: an Override silently hid every later Book Tier the reader set, a series rename orphaned it, and Settings Export and the Arrange View both had to carry it.

## Decision

A series' Tier is always the Book Tier of its Deciding Book: the highest-indexed book that is both read and tiered. On a tie at the same index, the book calibre modified most recently (`last_modified`) wins, then the higher book id. Date read plays no part. Overrides are removed: no menu entry, no prefs map, nothing in Settings Export. The Arrange View only reorders within a Lane, for Stacks and Cards alike.

## Considered Options

- **Latest date read decides.** Rejected: a reread of book 1 would drag the series back to a Tier the reader has moved past. Series index reflects how far they got.
- **Record when the plugin sets each Book Tier, for the tie-break.** Exact, but it adds stored state and tiers set before it have no stamp. Ties at one index are rare, so `last_modified` is good enough even though any metadata edit bumps it.
- **Dragging a Stack to another Lane sets the Deciding Book's Book Tier.** Rejected: one drag would quietly rewrite one book, which is hard to see from the board.

## Consequences

- Stored `series_tier_overrides` entries are ignored on read and dropped the next time Settings saves; imports skip them. No migration.
- The `override` field leaves the series object in Tier List Data and the schema version bumps.
- To move a series, the reader changes the Book Tier of its Deciding Book, which the Series Panel marks.

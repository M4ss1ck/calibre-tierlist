# 0001 Tier stored as id in a Text column

Status: Accepted
Date: 2026-11-05

## Context

Books need a Tier that is searchable and sortable in calibre, and a renamed or recoloured Tier must leave every book untouched. A column holding labels would rewrite every ranked book on each cosmetic edit, so the stored value and the displayed value have to be separate.

## Decision

Book Tier lives in a calibre Text custom column holding the Tier id from Tier Config, not the label. A Tier carries a stable id, label, colour, optional description, and position. The plugin offers to create the column on first run. One saved search per Tier, maintained by the plugin when tiers change, gives search by tier name from the calibre search bar.

## Consequences

- Renaming, recolouring, describing, and reordering a Tier write no books.
- A column value whose id is missing from Tier Config is a stale Book Tier. Removing a Tier that still holds books warns with the affected count, then clears those Book Tiers and leaves the books read.
- Showing a tier anywhere requires Tier Config: the column alone does not name a tier.
- Tier Config import/export must keep ids stable so books keep their tier when a Tier Config is reused.

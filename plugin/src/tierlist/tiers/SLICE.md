# SLICE: tiers

## Purpose

Holds the Tier Config: the ordered Tiers for one library, the custom column that stores each Book Tier, and the column that holds Read State. It is separate so every other slice, and the compiled board, can name a Tier without importing calibre.

## Public API

- `Tier`: one rank, with a stable id, the label a reader sees, a colour, and an optional description.
- `TierConfig`: the ordered Tiers plus the lookup names of the Text column holding Book Tier and the Date or Yes/No column holding Read State (default `#date_read`).
- `TierConfig.tier(tier_id) -> Tier | None`: the Tier that id names, in glossary terms a Book Tier resolved to its Tier.
- `TierConfig.to_dict()` / `TierConfig.from_dict(data)`: the JSON shape imported and exported between libraries.
- `DEFAULT_TIER_CONFIG`: S, A, B, C, D, F with conventional colours.

## Files

- `config.py`: `Tier`, `TierConfig`, and the default Tier Config.

## Depends on

- Ports: none; this slice is data, and prefs reach it only through the facade.
- Slices: none.
- Imports nothing from calibre or Qt.

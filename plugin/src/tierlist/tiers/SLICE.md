# SLICE: tiers

## Purpose

Holds the Tier Config: the ordered Tiers for one library, the custom column that stores each Book Tier, and the column that holds Read State. It is separate so every other slice, and the compiled board, can name a Tier without importing calibre.

## Public API

- `Tier`: one rank, with a stable id, the label a reader sees, a colour, and an optional description.
- `TierConfig`: the ordered Tiers plus the lookup names of the Text column holding Book Tier, the Date or Yes/No column holding Read State (default `#date_read`), the Stack depth (`stack_depth`), and the optional Integer column holding each series' total (`series_total_column`).
- `MIN_STACK_DEPTH` / `MAX_STACK_DEPTH` / `DEFAULT_STACK_DEPTH`: the Stack Depth bounds and default, 0, 6, and 3.
- `TierConfig.tier(tier_id) -> Tier | None`: the Tier that id names, in glossary terms a Book Tier resolved to its Tier.
- `TierConfig.to_dict()` / `TierConfig.from_dict(data)`: the JSON shape imported and exported between libraries.
- `TierConfigError`: a rejected Tier Config, with a message a reader can act on.
- `validate(config) -> None`: raise `TierConfigError` for no Tiers, duplicate or empty ids, empty labels, a colour that is not `#rrggbb`, or a Stack Depth outside `MIN_STACK_DEPTH`..`MAX_STACK_DEPTH`.
- `parse_config(text) -> TierConfig` / `dump_config(config) -> str`: JSON import and export; every parse failure becomes a `TierConfigError` with a human message.
- `DEFAULT_TIER_CONFIG`: S, A, B, C, D, F with conventional colours.

## Files

- `config.py`: `Tier`, `TierConfig`, and the default Tier Config.
- `validate.py`: `TierConfigError`, `validate`, `parse_config`, and `dump_config`.

## Depends on

- Ports: none; this slice is data, and prefs reach it only through the facade.
- Slices: none.
- Imports nothing from calibre or Qt.

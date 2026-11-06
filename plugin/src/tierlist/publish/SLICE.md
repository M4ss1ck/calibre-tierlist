# SLICE: publish

## Purpose

Writes the compiled board as one self-contained HTML file by embedding Tier List Data at the template's marker. It is separate so payload escaping and the file write stay calibre-free and the template stays a single built artifact.

## Public API

- `MARKER`: the token the template carries where the payload goes.
- `render_html(template, data) -> str`: replaces the marker with escaped JSON, raising ValueError unless it appears exactly once.
- `write_html(template, data, path) -> int`: renders, creates parent directories, writes UTF-8, and returns the byte size.

## Files

- `html.py`: marker injection, `</` escaping, and the UTF-8 file write.

## Depends on

- Ports: none.
- Slices: `compile` for `TierListData`.
- Imports nothing from calibre or Qt.

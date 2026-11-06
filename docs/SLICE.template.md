# SLICE: <slice name>

Copy this file to `<slice>/SLICE.md` when the slice is created. Keep it near 20 lines and treat it as a navigation brief, not a glossary: terms live in the root `GLOSSARY.md`.

## Purpose

<One or two sentences on the user-visible job this slice does and why it is separate. No implementation detail.>

## Public API

- `<function or type>(<args>) -> <result>`: <what a caller gets, named in glossary terms.>
- <Repeat per public entry point. Anything not listed here is internal and may change.>

## Files

- `<path>`: <one line of responsibility. Add each file here before writing it; 150 lines hard, 100 soft.>

## Depends on

- Ports: <Library, Covers, Prefs as used, or none. State why.>
- Slices: <other slices whose public API this one calls, or none.>
- <Core slices must not import calibre or Qt; only `calibre_ui` and port adapters may.>

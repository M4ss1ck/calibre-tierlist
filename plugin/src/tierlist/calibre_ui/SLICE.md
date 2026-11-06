# SLICE: calibre_ui

## Purpose

Adapts the calibre-free core to calibre's GUI: it registers the Tier List action and translates the strings a reader sees. It is separate so the core stays importable, and testable, without calibre or Qt.

## Public API

- `TierListAction`: the `InterfaceAction` that calibre instantiates through the zip root entry point.

## Files

- `action.py`: the action, its placeholder dialog, and the one-time toolbar and context menu claim.

## Depends on

- Ports: none yet; the layout claim is calibre GUI state, not Tier Config, so it calls `gprefs` directly.
- Slices: none yet.
- Imports calibre and Qt; the only slice allowed to.

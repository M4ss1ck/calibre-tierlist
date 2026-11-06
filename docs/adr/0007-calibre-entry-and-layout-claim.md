# 0007 calibre entry point and layout claim

Status: Accepted
Date: 2026-11-05

## Context

calibre loads a plugin zip by executing its root `__init__.py`, which must expose an `InterfaceActionBase`. The core still has to stay importable in a plain interpreter, without calibre or Qt, so tests can run it. calibre-customize installs place no action on the toolbar or context menu, and calibre runs Python with `-OO`.

## Decision

The zip root `__init__.py` is built from `plugin/calibre_entry.py`, so `plugin/src/tierlist/__init__.py` stays calibre-free and tests import the core without calibre. `calibre_entry.py` is the only file outside `calibre_ui` that imports calibre.

`TierListAction.genesis` appends `Tier List` to `gprefs['action-layout-toolbar']` and `gprefs['action-layout-context-menu']`, once, guarded by `gprefs['tierlist-layouts-claimed']`. The guard is never cleared, so a user who removes the entry never gets it back. This is calibre GUI state, not Tier Config, so it does not go through the Prefs port.

Plugin and itest code must not use `assert`, because `-OO` strips it.

## Consequences

- Unit tests cover the core without a calibre install; the entry point is only exercised by the itest.
- Layout state lives in gprefs, so the Prefs port never sees it and the itest drives it directly.
- Sanity checks in the itest use an explicit `expect` helper instead of `assert`.

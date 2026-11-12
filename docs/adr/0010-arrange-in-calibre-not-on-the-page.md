# 0010 Arrange the board in calibre, not on the page

Status: Accepted
Date: 2026-11-11

## Context

Readers want to hand-order Stacks and Cards inside a Lane and drag a series or book to another Tier. The obvious place for drag and drop is the compiled page, which already draws the board. But the page is an offline `file://` document (ADR 0005) and cannot write back to calibre, and Lane Order, Overrides and Book Tiers all live in calibre (ADR 0001, 0002).

## Decision

Dragging happens in the Arrange View, a Qt part of the Settings dialog that draws the board from the same compile used for the page. A drop there writes straight to per-library prefs (Lane Order, Overrides) or the Tier column (Book Tier) when Settings is saved. The compiled page stays read-only for arrangement: it draws Lanes in the order the payload gives.

## Considered Options

- **Drag on the page, then copy the arrangement into calibre as JSON.** Two steps for every change, and a forgotten paste silently loses work.
- **The plugin serves the page on localhost so it can save back.** Adds a port, a server lifecycle and a security surface to a plugin that otherwise never opens a socket.
- **Page-side localStorage.** Lost when the file moves, and invisible to calibre and to the next compile.

## Consequences

- The Arrange View needs covers in Qt, read through the existing `Covers` port, sized small and loaded lazily so a 1,000-book library stays responsive.
- Lane Order keys series by name, like Overrides, so renaming a series loses its place. It goes to the end of its Lane instead of becoming an orphan, and stale names are pruned on save.
- Reordering on the page would need this ADR revisited; on-page renames and filters are unaffected.

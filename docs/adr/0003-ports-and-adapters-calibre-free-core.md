# 0003 Ports and adapters with a calibre-free core

Status: Accepted
Date: 2026-11-05

## Context

The core domain must be testable in a plain Python environment in under 2 seconds and must import nothing from calibre or Qt. Calibre APIs exist only inside the running application, so the domain cannot call them directly.

## Decision

The ports, each with a calibre adapter and an in-memory fake:

- Library: list books in a Compile Scope with the fields the domain needs; write Book Tier and Read State for a set of book ids; list series names and every book id.
- Covers: `formats()` lists the image formats the host can encode, and `cover(book_id, fmt, width)` returns an encoded thumbnail and its dominant colour.
- Prefs: read and write Tier Config and Series Tier Overrides for the current library.
- SavedSearches: list saved search names, read a query, and add, remove, or rename a search; the config dialog keeps one `Tier <label>` search per Tier.

The application facade, constructed with the ports, exposes the book and compile use cases: set and clear Book Tier, mark read, mark unread, set and clear a Series Tier Override, and compile a Compile Scope into Tier List Data. Covers defaults to a null port that has no covers, so use cases that never compile need not pass it. The calibre UI calls only this facade.

The config dialog uses a second facade, `ConfigAdmin`, over Library, Prefs, and SavedSearches: it validates and saves Tier Config, imports and exports JSON, counts the books a Tier holds, syncs saved searches, and lists, reattaches, or deletes orphaned Overrides.

## Consequences

- The core slices (tiers, marking, catalog, compile, covers, publish) import nothing from calibre or Qt.
- Only `calibre_ui` and the port adapters import calibre or Qt.
- Domain behaviour is tested through the facade with fakes; the same facade scenarios rerun under calibre-debug with the real adapters for the integration lane.
- A new capability means a new port method and both implementations, which keeps the seam explicit.

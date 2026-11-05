# 0003 Ports and adapters with a calibre-free core

Status: Accepted
Date: 2026-11-05

## Context

The core domain must be testable in a plain Python environment in under 2 seconds and must import nothing from calibre or Qt. Calibre APIs exist only inside the running application, so the domain cannot call them directly.

## Decision

Three ports, each with a calibre adapter and an in-memory fake:

- Library: list books in a Compile Scope with the fields the domain needs; write Book Tier and Read State for a set of book ids; list series names.
- Covers: given a book id, return an encoded thumbnail and its dominant colour, or nothing.
- Prefs: read and write Tier Config and Series Tier Overrides for the current library.

A single application facade, constructed with the three ports, exposes every use case: get and save Tier Config with validation, import and export Tier Config, set and clear Book Tier, mark read, mark unread, set and clear a Series Tier Override, list orphaned overrides, and compile a Compile Scope into Tier List Data. The calibre UI calls only this facade.

## Consequences

- The core slices (tiers, marking, catalog, compile, covers, publish) import nothing from calibre or Qt.
- Only `calibre_ui` and the port adapters import calibre or Qt.
- Domain behaviour is tested through the facade with fakes; the same facade scenarios rerun under calibre-debug with the real adapters for the integration lane.
- A new capability means a new port method and both implementations, which keeps the seam explicit.

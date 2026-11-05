# 0002 Per-library prefs for Tier Config and overrides

Status: Accepted
Date: 2026-11-05

## Context

A reader can hold several calibre libraries and wants each to have its own tier scheme. Series Tier Overrides follow a series, not a book, so they cannot live on a book row. Book Tier and Read State already live in custom columns (see 0001), which keeps them searchable and sortable.

## Decision

Tier Config, meaning the ordered Tiers plus plugin settings (column mapping, stack depth), lives in calibre's per-library namespaced prefs under the `tierlist` namespace. Series Tier Overrides live there too, keyed by series name. All reads and writes go through the Prefs port. A scheme moves between libraries only by export and import as JSON.

## Consequences

- Switching library switches tier scheme; no library sees another library's Tiers or Overrides.
- Renaming a series can orphan its Override. The config UI lists overrides that no longer match any series so the reader can reattach or delete them.
- Book Tier and Read State stay in columns, so they follow the library rather than the prefs entry.
- Tests replace the Prefs port with an in-memory fake; no test touches calibre prefs.

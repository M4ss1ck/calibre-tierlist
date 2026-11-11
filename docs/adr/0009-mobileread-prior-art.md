# 0009 MobileRead prior art: no equivalent plugin

Status: Accepted
Date: 2026-11-11

## Context

Issue #15 asks whether a calibre plugin already does what this one does, before we build it. Three sources were checked: the MobileRead "Index of plugins" thread (https://www.mobileread.com/forums/showthread.php?t=118764), calibre's machine-readable plugin index (https://plugins.calibre-ebook.com/, 254 entries with version, release date and thread link), and all 1,088 thread titles in the Calibre Plugins forum (f=237, sorted by title, 12 pages). No index entry describes a tier board, and no thread title contains "tier" or "rank". The check is title- and description-level: a plugin whose thread title hides a ranking feature would not surface, and threads outside f=237 are not covered.

## Decision

Nothing equivalent exists, so this ships as a new plugin. The nearest neighbours, dated by their latest release unless noted:

- **Review Nook** — https://www.mobileread.com/forums/showthread.php?t=375545 — rich-text reviews, half-star personal ratings, recommendation flag, dashboard, CSV/XLSX/HTML export.
- **GRating Rebalancer** — https://www.mobileread.com/forums/showthread.php?t=373799 — Goodreads ratings reshaped into library-relative percentiles in a column.
- **Reading List** — https://www.mobileread.com/forums/showthread.php?t=134856 — several orderable lists per device, synced, filled by tag or custom column.
- **Manage Series** — https://www.mobileread.com/forums/showthread.php?t=125729 — drag-and-drop renumbering and reordering of series.
- **Book List Plus** — https://www.mobileread.com/forums/showthread.php?t=373100 — cover-grid view of the library.
- **Goodreads Sync** — https://www.mobileread.com/forums/showthread.php?t=123281 — shelves mapped to tags and custom columns.
- **Count Pages** — https://www.mobileread.com/forums/showthread.php?t=134000 — page and word counts into columns.
- **Float Rating** — https://www.mobileread.com/forums/showthread.php?t=325652 — decimal ratings into a column; deprecated, last activity 26 Sep 2020.

What separates this plugin, in the terms of `GLOSSARY.md:23-33` and ADR 0005:

- It is the only one storing a user-chosen Tier id in a text column and rolling it up to a Series Tier, by Auto majority or per-series Override.
- It is the only one compiling a standalone offline HTML board with lanes, fanned Stacks, and empty slots for unowned positions; the neighbours act inside calibre's GUI.
- It exports that board as PNG and PDF in the browser; no neighbour exports a visual ranking.
- Neighbours rate (Review Nook, GRating Rebalancer), order (Reading List, Manage Series), or show the library (Book List Plus); none draws a tier ladder.

## Consequences

- The plugin's name and thread must say "tier list" plainly, since no existing thread trains users to look for it.
- A neighbour that gains series-level ranking or a board export later is a real overlap, and the comparison above is the baseline to recheck.
- The check is cheap to repeat: the index and the forum title listing are both scriptable, so a reread before a major release costs minutes.

# 0008 snapdom for the PNG snapshot

Status: Accepted
Date: 2026-11-11

## Context

ADR 0005 leaves the snapshot library open between snapdom and modern-screenshot. The page must render the live board — inline theme, `data:` cover images, expanded Stacks — to a PNG in the browser, offline, at the scale the export planner sets, and leave the export control out of the picture. The board can hold hundreds of Cards, so capture speed matters.

## Decision

Export uses snapdom (`@zumer/snapdom`, pinned). It has no runtime dependencies, captures large DOMs quickly, takes a CSS selector in `exclude` (the control is marked `data-export-skip`), and is actively maintained. modern-screenshot would also work and remains a reasonable fallback.

## Consequences

- vite bundles the library into the single HTML file, so export works offline like the rest of the page.
- `snapshot.ts` is a thin adapter: the scale, the exclusion and the page background are the only options it sets, and webfont discovery is off.
- Swapping libraries later touches one file.

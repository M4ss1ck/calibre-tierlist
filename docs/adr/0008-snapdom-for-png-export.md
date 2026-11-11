# 0008 snapdom for the PNG snapshot

Status: Accepted
Date: 2026-11-11

## Context

ADR 0005 leaves the snapshot library open between snapdom and modern-screenshot. The page must render the live board — inline theme, `data:` cover images, expanded Stacks — to a PNG in the browser, offline, at the scale the export planner sets. The board can hold hundreds of Cards, so capture speed matters.

## Decision

Export uses snapdom (`@zumer/snapdom`, pinned). It has no runtime dependencies, captures large DOMs quickly, is actively maintained, and reports a capture's degradations as warning codes, so a fallback surfaces in the status line instead of passing silently. modern-screenshot would also work and remains a reasonable fallback.

## Consequences

- vite bundles the library into the single HTML file, so export works offline like the rest of the page.
- `snapshot.ts` is a thin adapter: the scale, `dpr` and the page background are the only options it sets, webfont discovery is off, and the capture's warning codes reach `exportPng`'s status message.
- `dpr: 1` is pinned because the planner already folds devicePixelRatio into `scale`.
- Swapping libraries later touches one file, plus the reading of the warnings it hands back.

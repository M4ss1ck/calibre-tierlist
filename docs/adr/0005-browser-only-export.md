# 0005 Export lives in the browser only

Status: Accepted
Date: 2026-11-05

## Context

The page must export the board as PNG and as PDF, and the export must reflect the current filters and theme. The plugin ships zero runtime dependencies beyond calibre, and a PDF or image export path inside calibre is out of scope. The HTML must work offline with zero network requests.

## Decision

Export is a web feature. For PNG, the template bundles a DOM snapshot library (snapdom or modern-screenshot) and renders the current filtered view and theme. When the board would exceed a safe canvas size, the page exports one PNG per Tier and bundles them into a zip. For PDF, the page uses a print stylesheet and the browser print dialog. The plugin writes only the HTML file and has no export path of its own.

## Consequences

- The exported PNG matches what the reader sees, including filters and theme.
- Large boards still export, per Tier and zipped, instead of failing silently at a canvas limit.
- PDF text and covers stay sharp at any zoom because the browser prints rather than rasterises the board.
- The snapshot library and its styles ship inside the single HTML file, so export works offline like the rest of the page.
- The plugin needs no image or PDF library beyond the cover encoder.

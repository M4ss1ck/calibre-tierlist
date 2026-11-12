# SLICE: export

## Purpose

Turns the compiled Sheet into a PNG the reader can keep: one image of the title, Lanes and footer when it fits what the browser can draw, otherwise one image per Lane bundled into a zip. It plans the canvas sizes in a pure function, snapshots a copy of the live DOM so filters, renamed labels and the theme apply as shown, and never fails silently — an export error, or a degradation snapdom reports, reaches the reader in the status message. It also owns the print stylesheet, so the same board prints to a readable PDF.

## Public API

- `Size`: a width and height in CSS pixels.
- `Limits` and `SAFE_LIMITS`: the `maxSide` and `maxArea` caps a canvas may not exceed, and the conservative pair every browser accepts (Safari's 4096x4096 area cap is the strictest).
- `ExportPlan`: either `{ kind: "single", scale }` for the whole board, or `{ kind: "split", parts }` with one part per Lane.
- `ExportPart`: a Lane's `id`, the `scale` to draw it at, and whether it was `downscaled`.
- `fits(size, scale, limits) -> boolean`: both scaled sides are within `maxSide` and the scaled area within `maxArea`.
- `fitScale(size, limits) -> number`: the largest scale the size fits at, the tightest of the side and area caps.
- `planExport(board, lanes, scale, limits = SAFE_LIMITS) -> ExportPlan`: the board as a single canvas when it fits, else one part per Lane in input order, each keeping `scale` when it fits or taking `fitScale` and marked downscaled.
- `Snapshot`: a captured PNG `blob` and the unique warning codes snapdom recorded for it.
- `snapshot(element, scale) -> Promise<Snapshot>`: renders the element to a PNG at `scale` and returns its `blob` with the unique warning codes snapdom recorded; no network.
- `SCREEN_ONLY` and `stage(sheet) -> Staged`: the selectors the image leaves out (`.controls`, `form.filters`), and an inert, `aria-hidden` copy of the sheet without them, laid out off screen at the sheet's width so the layout closes up where they were; `dispose()` removes it.
- `exportPng(sheet) -> Promise<string>`: stages the sheet, measures the copy and its `[data-lane-id]` Lanes, plans at `max(1, devicePixelRatio)`, downloads `tierlist.png` (the whole board, or the one Lane of a split plan) or `tierlist.zip` (entries `NN-<laneId>.png` in Lane order), and resolves to the status message, noting any shrunk Lanes and any snapshot warnings. Rejects on failure.
- `ExportButton(board)`: the toolbar's "Download PNG" control, handed the `.sheet`; disabled and reading "Exporting…" while it runs, with the outcome in a visible `role="status"` element, and the same element says the board is not ready when it has none.
- `PdfButton()`: the toolbar's "Print or PDF" control; one click opens the browser's print dialog, where `print.css` is what the paper gets. No busy state and no status line.

## Files

- `plan.ts`: the caps, the `fits` and `fitScale` checks, and the planner; no DOM, no canvas, no Svelte.
- `snapshot.ts`: the snapdom adapter; sets the scale and `dpr: 1`, uses the page background, disables webfont discovery, and reports snapdom's warning codes.
- `stage.ts`: the off-screen copy without the screen-only parts.
- `export.ts`: the staging, measurement, plan, PNG or zip download, and the status message.
- `ExportButton.svelte`: the button, its busy state, and the status line.
- `PdfButton.svelte`: the "Print or PDF" button that calls `window.print()`; the print stylesheet does the rest.
- `print.css`: the `@media print` rules PDF export rests on — the toolbar, filters, Series Panel and Detail Panel drop out while the title and Lanes stay, the sheet takes the printable width, every Stack and Card keeps off a page break, the light palette (surfaces included) is forced whatever the screen shows, and the colours print exact. Imported once by `src/main.ts`; it changes nothing on screen.

## Depends on

- Ports: none; the browser DOM only.
- Slices: `board` for the `.sheet` element App hands over, its `.controls`, the Lane `data-lane-id` hook, and the `.stack`, `.card`, `dialog.series-panel` and `dialog.detail` markup `print.css` hides or keeps whole; `filter` for the `form.filters` element `print.css` hides; `theme` for the control tokens, the tokens `print.css` restates for light paper, and the page background that keeps the PNG readable.
- `@zumer/snapdom` for the capture and `fflate` for the zip; both are bundled into the single HTML file, so export stays offline.

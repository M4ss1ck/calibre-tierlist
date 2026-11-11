# SLICE: export

## Purpose

Turns the compiled board into a PNG the reader can keep: one image when the whole board fits what the browser can draw, otherwise one image per Lane bundled into a zip. It plans the canvas sizes in a pure function, snapshots the live DOM so filters, expanded Stacks and the theme apply as shown, and never fails silently — an export error reaches the reader as a status message.

## Public API

- `Size`: a width and height in CSS pixels.
- `Limits` and `SAFE_LIMITS`: the `maxSide` and `maxArea` caps a canvas may not exceed, and the conservative pair every browser accepts (Safari's 4096x4096 area cap is the strictest).
- `ExportPlan`: either `{ kind: "single", scale }` for the whole board, or `{ kind: "split", parts }` with one part per Lane.
- `ExportPart`: a Lane's `id`, the `scale` to draw it at, and whether it was `downscaled`.
- `fits(size, scale, limits) -> boolean`: both scaled sides are within `maxSide` and the scaled area within `maxArea`.
- `fitScale(size, limits) -> number`: the largest scale the size fits at, the tightest of the side and area caps.
- `planExport(board, lanes, scale, limits = SAFE_LIMITS) -> ExportPlan`: the board as a single canvas when it fits, else one part per Lane in input order, each keeping `scale` when it fits or taking `fitScale` and marked downscaled.
- `snapshot(element, scale) -> Promise<Blob>`: renders the element to a PNG at `scale`, leaving out anything marked `data-export-skip`; no network.
- `exportPng(board) -> Promise<string>`: measures the board and its `[data-lane-id]` Lanes, plans at `max(1, devicePixelRatio)`, downloads `tierlist.png` or `tierlist.zip` (entries `NN-<laneId>.png` in Lane order), and resolves to the status message. Rejects on failure.
- `ExportButton(board)`: the toolbar's "Export PNG" control; disabled and reading "Exporting…" while it runs, with the outcome in a visible `role="status"` element.

## Files

- `plan.ts`: the caps, the `fits` and `fitScale` checks, and the planner; no DOM, no canvas, no Svelte.
- `snapshot.ts`: the snapdom adapter; sets the scale, excludes `data-export-skip`, and disables webfont discovery.
- `export.ts`: the measurement, the plan, the PNG or zip download, and the status message.
- `ExportButton.svelte`: the button, its busy state, and the status line.

## Depends on

- Ports: none; the browser DOM only.
- Slices: `board` for the Lane `data-lane-id` hook and the board element App hands over; `theme` for the control tokens and the page background that keeps the PNG readable.
- `@zumer/snapdom` for the capture and `fflate` for the zip; both are bundled into the single HTML file, so export stays offline.

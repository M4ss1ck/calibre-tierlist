# SLICE: export

## Purpose

Plans how the compiled board becomes a PNG: one canvas when the whole board fits what the browser can draw, otherwise one canvas per Lane, downscaling only the Lanes that cannot fit. It is separate so the arithmetic of canvas size is a pure, testable function, decided before anything is drawn.

## Public API

- `Size`: a width and height in CSS pixels.
- `Limits` and `SAFE_LIMITS`: the `maxSide` and `maxArea` caps a canvas may not exceed, and the conservative pair every browser accepts (Safari's 4096x4096 area cap is the strictest).
- `ExportPlan`: either `{ kind: "single", scale }` for the whole board, or `{ kind: "split", parts }` with one part per Lane.
- `ExportPart`: a Lane's `id`, the `scale` to draw it at, and whether it was `downscaled`.
- `fits(size, scale, limits) -> boolean`: both scaled sides are within `maxSide` and the scaled area within `maxArea`.
- `fitScale(size, limits) -> number`: the largest scale the size fits at, the tightest of the side and area caps.
- `planExport(board, lanes, scale, limits = SAFE_LIMITS) -> ExportPlan`: the board as a single canvas when it fits, else one part per Lane in input order, each keeping `scale` when it fits or taking `fitScale` and marked downscaled.

## Files

- `plan.ts`: the caps, the `fits` and `fitScale` checks, and the planner; no DOM, no canvas, no Svelte.

## Depends on

- Ports: none.
- Slices: none; it takes plain pixel sizes.
- Nothing else: no DOM, no dependencies. The canvas that draws the plan goes in another slice.

/** A width and height in CSS pixels. */
export type Size = { width: number; height: number };

/** The caps one exported canvas may not exceed, in pixels. */
export type Limits = { maxSide: number; maxArea: number };

/** The strictest common caps: Safari refuses canvases past 4096x4096 of area. */
export const SAFE_LIMITS: Limits = { maxSide: 16384, maxArea: 16_777_216 };

/** One canvas of a split export: the Lane to draw at `scale`. */
export type ExportPart = { id: string; scale: number; downscaled: boolean };

/** How to draw the export: one canvas for the whole board, or one per Lane. */
export type ExportPlan =
  | { kind: 'single'; scale: number }
  | { kind: 'split'; parts: ExportPart[] };

/** Whether `size` at `scale` stays inside both caps. */
export function fits(size: Size, scale: number, limits: Limits): boolean {
  const width = size.width * scale;
  const height = size.height * scale;
  return width <= limits.maxSide && height <= limits.maxSide && width * height <= limits.maxArea;
}

/** The largest scale `size` fits at, so an oversized Lane can be shrunk least. */
export function fitScale(size: Size, limits: Limits): number {
  if (size.width <= 0 || size.height <= 0) return limits.maxSide;
  return Math.min(
    limits.maxSide / size.width,
    limits.maxSide / size.height,
    Math.sqrt(limits.maxArea / (size.width * size.height)),
  );
}

/**
 * Plans the export: one canvas when the whole board fits, otherwise one canvas
 * per Lane in order, keeping `scale` where it fits and shrinking only the rest.
 */
export function planExport(
  board: Size,
  lanes: { id: string; size: Size }[],
  scale: number,
  limits: Limits = SAFE_LIMITS,
): ExportPlan {
  if (fits(board, scale, limits)) return { kind: 'single', scale };
  return {
    kind: 'split',
    parts: lanes.map((lane) =>
      fits(lane.size, scale, limits)
        ? { id: lane.id, scale, downscaled: false }
        : { id: lane.id, scale: fitScale(lane.size, limits), downscaled: true },
    ),
  };
}

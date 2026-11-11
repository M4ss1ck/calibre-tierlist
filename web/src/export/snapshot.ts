import { snapdom } from '@zumer/snapdom';

/** One captured PNG and the unique snapshot degradations snapdom recorded. */
export type Snapshot = { blob: Blob; warnings: string[] };

/**
 * Renders `element` to a PNG Blob at `scale` device pixels per CSS pixel, and reports
 * any capture warning codes so a degradation never passes silently. It reads only the
 * live page — no fetch, no proxy and no webfont discovery — so the export stays offline.
 * Nodes matching `exclude` are left out of the image without leaving a gap.
 * `dpr: 1` is pinned because the planner already folds devicePixelRatio into `scale`.
 */
export async function snapshot(
  element: HTMLElement,
  scale: number,
  exclude: string[] = [],
): Promise<Snapshot> {
  const background = getComputedStyle(document.body).backgroundColor;
  const capture = await snapdom(element, {
    scale,
    dpr: 1,
    backgroundColor: background,
    embedFonts: false,
    reconcile: true, // pins boxes whose text would re-wrap in the clone
    exclude,
    excludeMode: 'remove',
  });
  const blob = await capture.toBlob({ format: 'png' });
  const warnings = [...new Set(capture.warnings.map(({ code }) => code))];
  return { blob, warnings };
}

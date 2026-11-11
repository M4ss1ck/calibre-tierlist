import { snapdom } from '@zumer/snapdom';

/**
 * Renders `element` to a PNG Blob at `scale` device pixels per CSS pixel, leaving
 * out anything marked `data-export-skip`. It reads only the live page — no fetch,
 * no proxy and no webfont discovery — so the export stays offline.
 */
export async function snapshot(element: HTMLElement, scale: number): Promise<Blob> {
  const background = getComputedStyle(document.body).backgroundColor;
  return snapdom.toBlob(element, {
    format: 'png',
    scale,
    dpr: 1,
    backgroundColor: background,
    exclude: '[data-export-skip]',
    embedFonts: false,
  });
}

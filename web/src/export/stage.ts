/** What the page shows but the image leaves out: the toolbar and the filters. */
export const SCREEN_ONLY = ['.controls', 'form.filters'];

/** A copy of the sheet laid out for export, and how to take it down again. */
export type Staged = { element: HTMLElement; dispose: () => void };

/**
 * Lays a copy of `sheet` out off screen at the sheet's width, without the
 * `SCREEN_ONLY` parts, so the export measures and draws exactly what the image
 * holds: the layout closes up where the controls were, and the canvas ends
 * where the copy does. The copy is inert and hidden from assistive technology;
 * call `dispose` once the capture is done.
 */
export function stage(sheet: HTMLElement): Staged {
  const copy = sheet.cloneNode(true) as HTMLElement;
  copy.querySelectorAll(SCREEN_ONLY.join(', ')).forEach((node) => node.remove());
  copy.setAttribute('aria-hidden', 'true');
  copy.inert = true;
  Object.assign(copy.style, {
    position: 'absolute',
    top: '0',
    left: '-100000px',
    width: `${sheet.getBoundingClientRect().width}px`,
    boxSizing: 'border-box',
  });
  (sheet.parentElement ?? document.body).append(copy);
  return { element: copy, dispose: () => copy.remove() };
}

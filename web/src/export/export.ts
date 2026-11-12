import { zipSync } from 'fflate';
import { planExport, type Size } from './plan';
import { snapshot } from './snapshot';
import { stage } from './stage';

/** A rendered Lane and the id it exports under. */
type LaneElement = { id: string; element: HTMLElement; size: Size };

/** The rendered size of an element in CSS pixels, including overflow. */
function measure(element: HTMLElement): Size {
  const rect = element.getBoundingClientRect();
  return {
    width: Math.max(rect.width, element.scrollWidth),
    height: Math.max(rect.height, element.scrollHeight),
  };
}

/** Hands `blob` to the browser as a download, then releases the object URL. */
function download(blob: Blob, name: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = name;
  link.style.display = 'none';
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 60_000);
}

/** The zip entry name for the Lane at `index`: `01-s.png`, and so on. */
function entryName(index: number, id: string): string {
  return `${String(index + 1).padStart(2, '0')}-${id}.png`;
}

/** A status note naming any snapshot warning code, or an empty string. */
function warningNote(warnings: Set<string>): string {
  return warnings.size > 0 ? ` (with warnings: ${[...warnings].join(', ')})` : '';
}

/**
 * Exports the sheet as `tierlist.png`, or — when the whole sheet would exceed the
 * safe canvas size — one PNG per Lane in `tierlist.zip`. Draws an off-screen copy
 * without the screen-only controls (see `stage`). Resolves to the status message
 * shown to the reader; failures reject so they are never silent.
 */
export async function exportPng(sheet: HTMLElement): Promise<string> {
  const staged = stage(sheet);
  try {
    return await exportStaged(staged.element);
  } finally {
    staged.dispose();
  }
}

/** Plans, captures and downloads the staged `board`. */
async function exportStaged(board: HTMLElement): Promise<string> {
  const lanes: LaneElement[] = [...board.querySelectorAll<HTMLElement>('[data-lane-id]')].map(
    (element) => ({ id: element.dataset['laneId'] ?? 'lane', element, size: measure(element) }),
  );
  const scale = Math.max(1, window.devicePixelRatio);
  const plan = planExport(measure(board), lanes.map(({ id, size }) => ({ id, size })), scale);
  const warnings = new Set<string>();

  if (plan.kind === 'single') {
    const shot = await snapshot(board, plan.scale);
    shot.warnings.forEach((code) => warnings.add(code));
    download(shot.blob, 'tierlist.png');
    return `Exported tierlist.png${warningNote(warnings)}`;
  }

  const lanesById = new Map(lanes.map((lane) => [lane.id, lane]));
  const shots: { id: string; blob: Blob }[] = [];
  let shrunk = 0;
  for (const part of plan.parts) {
    const lane = lanesById.get(part.id);
    if (!lane) throw new Error(`No Lane for export part ${part.id}`);
    if (part.downscaled) shrunk += 1;
    const shot = await snapshot(lane.element, part.scale);
    shot.warnings.forEach((code) => warnings.add(code));
    shots.push({ id: part.id, blob: shot.blob });
  }

  const note = `${shrunk > 0 ? ` (${shrunk} shrunk to fit)` : ''}${warningNote(warnings)}`;

  if (plan.parts.length === 1 && shots[0]) {
    download(shots[0].blob, 'tierlist.png');
    return `Exported tierlist.png${note}`;
  }

  const files: Record<string, Uint8Array> = {};
  for (const [index, shot] of shots.entries()) {
    files[entryName(index, shot.id)] = new Uint8Array(await shot.blob.arrayBuffer());
  }
  const zip = zipSync(files, { level: 0 });
  download(new Blob([zip], { type: 'application/zip' }), 'tierlist.zip');

  return `Exported ${plan.parts.length} lanes as tierlist.zip${note}`;
}

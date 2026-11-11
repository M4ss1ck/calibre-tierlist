import { zipSync } from 'fflate';
import { planExport, type Size } from './plan';
import { snapshot } from './snapshot';

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
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

/** The zip entry name for the Lane at `index`: `01-s.png`, and so on. */
function entryName(index: number, id: string): string {
  return `${String(index + 1).padStart(2, '0')}-${id}.png`;
}

/**
 * Exports the board as `tierlist.png`, or — when the whole board would exceed the
 * safe canvas size — one PNG per Lane in `tierlist.zip`. Resolves to the status
 * message shown to the reader; failures reject so they are never silent.
 */
export async function exportPng(board: HTMLElement): Promise<string> {
  const lanes: LaneElement[] = [...board.querySelectorAll<HTMLElement>('[data-lane-id]')].map(
    (element) => ({ id: element.dataset['laneId'] ?? 'lane', element, size: measure(element) }),
  );
  const scale = Math.max(1, window.devicePixelRatio);
  const plan = planExport(measure(board), lanes.map(({ id, size }) => ({ id, size })), scale);

  if (plan.kind === 'single') {
    download(await snapshot(board, plan.scale), 'tierlist.png');
    return 'Exported tierlist.png';
  }

  const files: Record<string, Uint8Array> = {};
  let shrunk = 0;
  for (const [index, part] of plan.parts.entries()) {
    const lane = lanes[index];
    if (!lane) throw new Error(`No Lane for export part ${part.id}`);
    if (part.downscaled) shrunk += 1;
    const png = await snapshot(lane.element, part.scale);
    files[entryName(index, part.id)] = new Uint8Array(await png.arrayBuffer());
  }

  const zip = zipSync(files, { level: 0 });
  download(new Blob([zip], { type: 'application/zip' }), 'tierlist.zip');

  const tiers = `${plan.parts.length} ${plan.parts.length === 1 ? 'tier' : 'tiers'}`;
  const note = shrunk > 0 ? ` (${shrunk} shrunk to fit)` : '';
  return `Exported ${tiers} as tierlist.zip${note}`;
}

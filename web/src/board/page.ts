import type { Lane, PageDefaults, Tier } from '../contract/tierlist';

/** The Lanes the page shows: every Lane except the Unranked one when it is off. */
export function shownLanes(lanes: Lane[], showUnranked: boolean): Lane[] {
  return showUnranked ? lanes : lanes.filter((lane) => lane.tier !== null);
}

/** One Lane as the page draws it: its id, what it holds and what its label cell shows. */
export type BoardLane = {
  id: string;
  lane: Lane;
  label: string;
  colour: string;
  description: string | null;
};

/**
 * The Lanes the page draws, in order, with the label the reader left (or the
 * Tier's) and the Tier's description when Tier descriptions are on.
 */
export function boardLanes(
  lanes: Lane[],
  tiers: Tier[],
  labels: Record<string, string>,
  view: Pick<PageDefaults, 'showUnranked' | 'showDescriptions'>,
): BoardLane[] {
  return shownLanes(lanes, view.showUnranked).map((lane) => {
    const id = lane.tier ?? 'unranked';
    const tier = tiers.find((candidate) => candidate.id === lane.tier);
    const description = tier?.description.trim() ?? '';

    return {
      id,
      lane,
      label: labels[id] ?? tier?.label ?? 'Unranked',
      colour: tier?.colour ?? '#8a8a94',
      description: view.showDescriptions && description !== '' ? description : null,
    };
  });
}

const plural = (count: number, one: string, many: string) => `${count} ${count === 1 ? one : many}`;

/** The header's meta line: the counts and/or the library name the reader kept. */
export function headerMeta(
  bookCount: number,
  seriesCount: number,
  libraryName: string,
  showCounts: boolean,
  showLibrary: boolean,
): string {
  const counts = showCounts ? [plural(bookCount, 'book', 'books'), plural(seriesCount, 'series', 'series')] : [];
  return [...counts, ...(showLibrary ? [libraryName] : [])].filter(Boolean).join(' · ');
}

/** The footer's left part: the library name when it is on, then when the page was compiled. */
export function footerMeta(libraryName: string, showLibrary: boolean, compiled: string): string {
  return [...(showLibrary ? [libraryName] : []), `compiled ${compiled}`].filter(Boolean).join(' · ');
}

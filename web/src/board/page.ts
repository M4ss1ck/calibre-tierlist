import type { Lane } from '../contract/tierlist';

/** The Lanes the page shows: every Lane except the Unranked one when it is off. */
export function shownLanes(lanes: Lane[], showUnranked: boolean): Lane[] {
  return showUnranked ? lanes : lanes.filter((lane) => lane.tier !== null);
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

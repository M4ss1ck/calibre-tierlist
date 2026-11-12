import type { Lane, PageDefaults } from '../contract/tierlist';
import type { ThemeChoice } from '../theme/theme';

/** The view a compiled page opens with, taken from the Page Defaults baked into its payload. */
export type InitialView = {
  theme: ThemeChoice;
  title: string;
  unrankedLabel: string;
  showUnranked: boolean;
  showCounts: boolean;
  showLibrary: boolean;
};

/** The page-only choices a compiled page starts from. */
export function initialView(defaults: PageDefaults): InitialView {
  return {
    theme: defaults.theme,
    title: defaults.title,
    unrankedLabel: defaults.unrankedLabel,
    showUnranked: defaults.showUnranked,
    showCounts: defaults.showCounts,
    showLibrary: defaults.showLibrary,
  };
}

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

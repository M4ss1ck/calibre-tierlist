import type { PageDefaults } from '../contract/tierlist';
import { COVER_SIZES, EMPTY_LANE_MODES, GAPS, PAGE_WIDTHS } from './view';

/** The values a compiled page falls back to when neither its payload nor the query supplies a choice. */
const BUILT_IN: PageDefaults = {
  theme: 'system',
  title: 'Tier List',
  unrankedLabel: 'Unranked',
  showUnranked: true,
  showCounts: true,
  showLibrary: true,
  pageWidth: 'normal',
  showLabels: true,
  showDescriptions: false,
  laneGap: 'none',
  emptyLane: 'default',
  emptyLaneText: '',
  showCaptions: true,
  showReadCount: true,
  showSheets: true,
  coverSize: 'normal',
  coverGap: 'normal',
};

/** The query's values, keeping the last one when a key repeats. */
function queryValues(search: string): Map<string, string> {
  const values = new Map<string, string>();
  for (const [key, value] of new URLSearchParams(search)) values.set(key, value);
  return values;
}

/** `value` when it is one of `allowed`, else `fallback`. */
function chosenOf<T>(allowed: readonly T[], value: string | undefined, fallback: T): T {
  return allowed.includes(value as T) ? (value as T) : fallback;
}

/** The chosen switch: 1 and true are on, 0 and false are off, anything else falls back. */
function chosenSwitch(value: string | undefined, fallback: boolean): boolean {
  if (value === '1' || value === 'true') return true;
  if (value === '0' || value === 'false') return false;
  return fallback;
}

/** The chosen text, blank ignored. */
function chosenText(value: string | undefined, fallback: string): string {
  return value !== undefined && value.trim() !== '' ? value : fallback;
}

/**
 * The Page Defaults one opening uses: a query key wins over the baked value, which wins over the
 * built-in default. Unknown keys and invalid values are ignored for that key only.
 */
export function resolvePageDefaults(baked: Partial<PageDefaults>, search: string): PageDefaults {
  const query = queryValues(search);
  const defaults: PageDefaults = { ...BUILT_IN, ...baked };

  return {
    theme: chosenOf(['system', 'light', 'dark'], query.get('theme'), defaults.theme),
    title: chosenText(query.get('title'), defaults.title),
    unrankedLabel: chosenText(query.get('unranked_label'), defaults.unrankedLabel),
    showUnranked: chosenSwitch(query.get('unranked'), defaults.showUnranked),
    showCounts: chosenSwitch(query.get('counts'), defaults.showCounts),
    showLibrary: chosenSwitch(query.get('library'), defaults.showLibrary),
    pageWidth: chosenOf(PAGE_WIDTHS, query.get('width'), defaults.pageWidth),
    showLabels: chosenSwitch(query.get('labels'), defaults.showLabels),
    showDescriptions: chosenSwitch(query.get('descriptions'), defaults.showDescriptions),
    laneGap: chosenOf(GAPS, query.get('lane_gap'), defaults.laneGap),
    emptyLane: chosenOf(EMPTY_LANE_MODES, query.get('empty'), defaults.emptyLane),
    emptyLaneText: chosenText(query.get('empty_text'), defaults.emptyLaneText),
    showCaptions: chosenSwitch(query.get('captions'), defaults.showCaptions),
    showReadCount: chosenSwitch(query.get('read_count'), defaults.showReadCount),
    showSheets: chosenSwitch(query.get('sheets'), defaults.showSheets),
    coverSize: chosenOf(COVER_SIZES, query.get('cover_size'), defaults.coverSize),
    coverGap: chosenOf(GAPS, query.get('cover_gap'), defaults.coverGap),
  };
}

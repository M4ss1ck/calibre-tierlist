import type { PageDefaults } from '../contract/tierlist';

/** The built-in Empty Lane Message. */
export const EMPTY_LANE_TEXT = 'No books in this tier';

/** The text an empty Lane shows, or null when the reader hid it. */
export function emptyMessage(view: Pick<PageDefaults, 'emptyLane' | 'emptyLaneText'>): string | null {
  if (view.emptyLane === 'hidden') return null;
  if (view.emptyLane === 'custom') return view.emptyLaneText.trim() || EMPTY_LANE_TEXT;
  return EMPTY_LANE_TEXT;
}

/** One choice a View Panel control offers: its Page Defaults value and the label it shows. */
export type Option<T> = { value: T; label: string };

/** The Lane Gap and Cover Gap choices, in contract order. */
export const GAP_OPTIONS: Option<PageDefaults['laneGap']>[] = [
  { value: 'none', label: 'None' },
  { value: 'small', label: 'Small' },
  { value: 'normal', label: 'Normal' },
  { value: 'large', label: 'Large' },
];

/** The Cover Size choices, in contract order. */
export const COVER_SIZE_OPTIONS: Option<PageDefaults['coverSize']>[] = [
  { value: 'small', label: 'Small' },
  { value: 'normal', label: 'Normal' },
  { value: 'large', label: 'Large' },
];

/** The Page Width choices, in contract order. */
export const PAGE_WIDTH_OPTIONS: Option<PageDefaults['pageWidth']>[] = [
  { value: 'narrow', label: 'Narrow' },
  { value: 'normal', label: 'Normal' },
  { value: 'wide', label: 'Wide' },
  { value: 'full', label: 'Full' },
];

/** The Empty Lane Message modes, in contract order. */
export const EMPTY_LANE_MODES: PageDefaults['emptyLane'][] = ['default', 'hidden', 'custom'];

const values = <T>(options: Option<T>[]): T[] => options.map((option) => option.value);
export const GAPS = values(GAP_OPTIONS);
export const COVER_SIZES = values(COVER_SIZE_OPTIONS);
export const PAGE_WIDTHS = values(PAGE_WIDTH_OPTIONS);

const PAGE_WIDTH = { narrow: '60rem', normal: '85rem', wide: '110rem', full: 'none' } as const;
const COVER_SCALE = { small: '0.8', normal: '1', large: '1.25' } as const;
const COVER_GAP = {
  none: ['0rem', '0rem'],
  small: ['0.5rem', '0.75rem'],
  normal: ['0.875rem', '1.375rem'],
  large: ['1.5rem', '2rem'],
} as const;
const LANE_GAP = { none: '0rem', small: '0.5rem', normal: '1rem', large: '1.75rem' } as const;

/** The inline style, as CSS custom properties, that draws the board at these Page Defaults. */
export function viewStyle(
  view: Pick<PageDefaults, 'pageWidth' | 'coverSize' | 'coverGap' | 'laneGap'>,
): string {
  const [gapY, gapX] = COVER_GAP[view.coverGap];

  return [
    `--page-width: ${PAGE_WIDTH[view.pageWidth]}`,
    `--cover-scale: ${COVER_SCALE[view.coverSize]}`,
    `--cover-gap-y: ${gapY}`,
    `--cover-gap-x: ${gapX}`,
    `--lane-gap: ${LANE_GAP[view.laneGap]}`,
  ].join('; ');
}

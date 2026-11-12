import { describe, expect, it } from 'vitest';
import { EMPTY_LANE_TEXT, emptyMessage, viewStyle } from './view';

const lane = { emptyLane: 'default', emptyLaneText: '' } as const;
const style = { pageWidth: 'normal', coverSize: 'normal', coverGap: 'normal', laneGap: 'none' } as const;

describe('emptyMessage', () => {
  it('shows the built-in text by default', () => {
    expect(emptyMessage(lane)).toBe('No books in this tier');
    expect(EMPTY_LANE_TEXT).toBe('No books in this tier');
  });

  it('shows nothing when hidden', () => {
    expect(emptyMessage({ emptyLane: 'hidden', emptyLaneText: 'Nothing here' })).toBeNull();
  });

  it("shows the reader's own text when custom, trimmed", () => {
    expect(emptyMessage({ emptyLane: 'custom', emptyLaneText: '  Nothing yet  ' })).toBe('Nothing yet');
  });

  it('falls back to the built-in text when the custom text is blank', () => {
    expect(emptyMessage({ emptyLane: 'custom', emptyLaneText: '   ' })).toBe('No books in this tier');
  });
});

describe('viewStyle', () => {
  const full = { pageWidth: 'full', coverSize: 'small', coverGap: 'large', laneGap: 'small' } as const;

  it('draws the default view at the built-in size and gaps', () => {
    const expected =
      '--page-width: 85rem; --cover-scale: 1; --cover-gap-y: 0.875rem; --cover-gap-x: 1.375rem; --lane-gap: 0rem';
    expect(viewStyle(style)).toBe(expected);
  });

  it('draws a full page of small covers with a large Cover Gap and a small Lane Gap', () => {
    const expected =
      '--page-width: none; --cover-scale: 0.8; --cover-gap-y: 1.5rem; --cover-gap-x: 2rem; --lane-gap: 0.5rem';
    expect(viewStyle(full)).toBe(expected);
  });
});

import { describe, expect, it } from 'vitest';
import type { PageDefaults } from '../contract/tierlist';
import { resolvePageDefaults } from './query';

/** Every field non-default, so an override has to move it and an invalid value has to leave it. */
const baked: PageDefaults = {
  theme: 'light',
  title: 'My shelf',
  unrankedLabel: 'Someday',
  showUnranked: false,
  showCounts: false,
  showLibrary: false,
  pageWidth: 'wide',
  showLabels: false,
  showDescriptions: true,
  laneGap: 'large',
  emptyLane: 'hidden',
  emptyLaneText: 'Nothing here',
  showCaptions: false,
  showReadCount: false,
  coverSize: 'large',
  coverGap: 'small',
};

describe('resolvePageDefaults, the board view keys', () => {
  it('overrides the page width, ignoring an invalid one', () => {
    expect(resolvePageDefaults(baked, '?width=narrow').pageWidth).toBe('narrow');
    expect(resolvePageDefaults(baked, '?width=huge').pageWidth).toBe('wide');
  });

  it('overrides whether Lane labels show, ignoring an invalid switch', () => {
    expect(resolvePageDefaults(baked, '?labels=1').showLabels).toBe(true);
    expect(resolvePageDefaults(baked, '?labels=maybe').showLabels).toBe(false);
  });

  it('overrides whether Tier descriptions show, ignoring an invalid switch', () => {
    expect(resolvePageDefaults(baked, '?descriptions=0').showDescriptions).toBe(false);
    expect(resolvePageDefaults(baked, '?descriptions=maybe').showDescriptions).toBe(true);
  });

  it('overrides the Lane Gap, ignoring an invalid one', () => {
    expect(resolvePageDefaults(baked, '?lane_gap=small').laneGap).toBe('small');
    expect(resolvePageDefaults(baked, '?lane_gap=huge').laneGap).toBe('large');
  });

  it('overrides the Empty Lane Message choice, ignoring an invalid one', () => {
    expect(resolvePageDefaults(baked, '?empty=custom').emptyLane).toBe('custom');
    expect(resolvePageDefaults(baked, '?empty=sometimes').emptyLane).toBe('hidden');
  });

  it('overrides the custom Empty Lane Message text, ignoring a blank one', () => {
    expect(resolvePageDefaults(baked, '?empty_text=Nothing%20yet').emptyLaneText).toBe('Nothing yet');
    expect(resolvePageDefaults(baked, '?empty_text=%20%20').emptyLaneText).toBe('Nothing here');
  });

  it('overrides whether Captions show, ignoring an invalid switch', () => {
    expect(resolvePageDefaults(baked, '?captions=1').showCaptions).toBe(true);
    expect(resolvePageDefaults(baked, '?captions=yes').showCaptions).toBe(false);
  });

  it('overrides whether Read Counts show, ignoring an invalid switch', () => {
    expect(resolvePageDefaults(baked, '?read_count=1').showReadCount).toBe(true);
    expect(resolvePageDefaults(baked, '?read_count=yes').showReadCount).toBe(false);
  });

  it('ignores the retired sheets switch', () => {
    expect(resolvePageDefaults(baked, '?sheets=true')).toEqual(baked);
  });

  it('overrides the Cover Size, ignoring an invalid one', () => {
    expect(resolvePageDefaults(baked, '?cover_size=small').coverSize).toBe('small');
    expect(resolvePageDefaults(baked, '?cover_size=huge').coverSize).toBe('large');
  });

  it('overrides the Cover Gap, ignoring an invalid one', () => {
    expect(resolvePageDefaults(baked, '?cover_gap=large').coverGap).toBe('large');
    expect(resolvePageDefaults(baked, '?cover_gap=huge').coverGap).toBe('small');
  });
});

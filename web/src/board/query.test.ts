import { describe, expect, it } from 'vitest';
import type { PageDefaults } from '../contract/tierlist';
import { resolvePageDefaults } from './query';

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

describe('resolvePageDefaults', () => {
  it('changes nothing when the search is empty', () => {
    expect(resolvePageDefaults(baked, '')).toEqual(baked);
    expect(resolvePageDefaults(baked, '?')).toEqual(baked);
  });

  it('overrides the theme', () => {
    expect(resolvePageDefaults(baked, '?theme=dark')).toEqual({ ...baked, theme: 'dark' });
  });

  it('overrides the title', () => {
    expect(resolvePageDefaults(baked, '?title=Best%20of%202026')).toEqual({ ...baked, title: 'Best of 2026' });
  });

  it('overrides the Unranked Lane label', () => {
    expect(resolvePageDefaults(baked, '?unranked_label=Later')).toEqual({ ...baked, unrankedLabel: 'Later' });
  });

  it('overrides the header switches', () => {
    expect(resolvePageDefaults(baked, '?unranked=1')).toEqual({ ...baked, showUnranked: true });
    expect(resolvePageDefaults(baked, '?counts=true')).toEqual({ ...baked, showCounts: true });
    expect(resolvePageDefaults(baked, '?library=1')).toEqual({ ...baked, showLibrary: true });
  });

  it('turns a switch off with 0 or false', () => {
    const on: PageDefaults = { ...baked, showUnranked: true, showCounts: true, showLibrary: true };

    expect(resolvePageDefaults(on, '?unranked=0')).toEqual({ ...on, showUnranked: false });
    expect(resolvePageDefaults(on, '?counts=false')).toEqual({ ...on, showCounts: false });
    expect(resolvePageDefaults(on, '?library=0')).toEqual({ ...on, showLibrary: false });
  });

  it('ignores an invalid value for that key only', () => {
    expect(resolvePageDefaults(baked, '?theme=blue&counts=1')).toEqual({ ...baked, showCounts: true });
    expect(resolvePageDefaults(baked, '?counts=maybe&library=1')).toEqual({ ...baked, showLibrary: true });
  });

  it('ignores an empty title or Unranked Lane label', () => {
    expect(resolvePageDefaults(baked, '?title=')).toEqual(baked);
    expect(resolvePageDefaults(baked, '?title=%20%20')).toEqual(baked);
    expect(resolvePageDefaults(baked, '?unranked_label=')).toEqual(baked);
  });

  it('ignores unknown keys', () => {
    expect(resolvePageDefaults(baked, '?sort=name&theme=dark')).toEqual({ ...baked, theme: 'dark' });
  });

  it('uses the last of repeated keys', () => {
    expect(resolvePageDefaults(baked, '?theme=dark&theme=system')).toEqual({ ...baked, theme: 'system' });
    expect(resolvePageDefaults(baked, '?title=First&title=Last')).toEqual({ ...baked, title: 'Last' });
    expect(resolvePageDefaults(baked, '?counts=0&counts=1')).toEqual({ ...baked, showCounts: true });
  });

  it('falls back to the built-in default when the baked value is missing', () => {
    expect(resolvePageDefaults({}, '')).toEqual({
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
      coverSize: 'normal',
      coverGap: 'normal',
    });
  });
});

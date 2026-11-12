import { describe, expect, it } from 'vitest';
import type { Lane } from '../contract/tierlist';
import { footerMeta, headerMeta, shownLanes } from './page';

const lanes: Lane[] = [
  { tier: 's', items: [] },
  { tier: null, items: [] },
];

describe('shownLanes', () => {
  it('drops the Unranked Lane when it is off', () => {
    expect(shownLanes(lanes, false)).toEqual([lanes[0]]);
  });

  it('keeps every Lane when it is on', () => {
    expect(shownLanes(lanes, true)).toEqual(lanes);
  });
});

describe('headerMeta', () => {
  it('shows the counts then the library name', () => {
    expect(headerMeta(1, 2, 'Lib', true, true)).toBe('1 book · 2 series · Lib');
  });

  it('drops the counts and the library name when they are off', () => {
    expect(headerMeta(1, 2, 'Lib', false, false)).toBe('');
  });

  it('keeps only the part that is still on', () => {
    expect(headerMeta(4, 2, 'Lib', false, true)).toBe('Lib');
    expect(headerMeta(4, 2, 'Lib', true, false)).toBe('4 books · 2 series');
  });
});

describe('footerMeta', () => {
  it('shows the library name then when the page was compiled', () => {
    expect(footerMeta('Lib', true, '6 Nov 2026')).toBe('Lib · compiled 6 Nov 2026');
  });

  it('drops the library name when it is off', () => {
    expect(footerMeta('Lib', false, '6 Nov 2026')).toBe('compiled 6 Nov 2026');
  });
});

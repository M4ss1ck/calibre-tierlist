import { describe, expect, it } from 'vitest';
import type { Lane, Tier } from '../contract/tierlist';
import { boardLanes, footerMeta, headerMeta, shownLanes } from './page';

const lanes: Lane[] = [
  { tier: 's', items: [] },
  { tier: 'a', items: [] },
  { tier: null, items: [] },
];
const tiers: Tier[] = [
  { id: 's', label: 'S', colour: '#ff0000', description: 'The best' },
  { id: 'a', label: 'A', colour: '#00ff00', description: '  ' },
];
const off = { showUnranked: false, showDescriptions: false };
const on = { showUnranked: true, showDescriptions: true };

describe('shownLanes', () => {
  it('drops the Unranked Lane when it is off', () => {
    expect(shownLanes(lanes, false)).toEqual([lanes[0], lanes[1]]);
  });

  it('keeps every Lane when it is on', () => {
    expect(shownLanes(lanes, true)).toEqual(lanes);
  });
});

describe('boardLanes', () => {
  it('names each Lane after its Tier, with the Tier colour and no description', () => {
    expect(boardLanes(lanes, tiers, {}, off)).toEqual([
      { id: 's', lane: lanes[0], label: 'S', colour: '#ff0000', description: null },
      { id: 'a', lane: lanes[1], label: 'A', colour: '#00ff00', description: null },
    ]);
  });

  it('keeps a renamed label and the Unranked Lane, which has no description', () => {
    const drawn = boardLanes(lanes, tiers, { a: 'Renamed', unranked: 'Someday' }, on);
    expect(drawn.map(({ id, label }) => [id, label])).toEqual([
      ['s', 'S'],
      ['a', 'Renamed'],
      ['unranked', 'Someday'],
    ]);
    expect(drawn.map(({ description }) => description)).toEqual(['The best', null, null]);
    expect(drawn[2]?.colour).toBe('#8a8a94');
  });

  it('leaves a blank Tier description out', () => {
    const [, a] = boardLanes(lanes, tiers, {}, on);
    expect(a?.description).toBeNull();
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

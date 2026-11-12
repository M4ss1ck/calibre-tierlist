import { describe, expect, it } from 'vitest';
import type { Book } from '../contract/tierlist';
import { back, closeDetail, closePanel, openPicked, pick, type Nav } from './dialogs';

const book: Book = {
  title: 'Dune Messiah',
  authors: [],
  series: 'Dune',
  seriesIndex: '2',
  rating: null,
  tags: [],
  blurb: null,
  tier: null,
  dateRead: null,
  read: true,
};
const from = { series: 'Dune', row: 2 };

describe('dialogs', () => {
  it('opens a Stack as its Series Panel with no row to focus', () => {
    expect(openPicked({ focusRow: 1 }, { stack: 'Dune' })).toEqual({ opened: 'Dune', focusRow: undefined });
  });

  it('closes the panel as soon as a row opens Detail', () => {
    const nav = pick(openPicked({}, { stack: 'Dune' }), { book }, from);
    expect(nav.opened).toBeUndefined();
    expect(nav.selection).toEqual({ book });
  });

  it('opens a Card in Detail with no way back', () => {
    const nav = openPicked(pick({}, { book }, from), { book });
    expect(nav.selection).toEqual({ book });
    expect(nav.returnTo).toBeUndefined();
  });

  it('goes back from Detail to the panel it came from, on the row that opened it', () => {
    let nav: Nav = pick(openPicked({}, { stack: 'Dune' }), { book }, from);

    nav = back(nav);
    expect(nav).toEqual({ opened: 'Dune', focusRow: 2, selection: undefined, returnTo: undefined });
    expect(closeDetail(nav)).toEqual({ opened: 'Dune', focusRow: 2, selection: undefined, returnTo: undefined });
  });

  it('forgets the way back once Detail closes any other way', () => {
    const nav = back(closeDetail(pick({}, { book }, from)));
    expect(nav.opened).toBeUndefined();
  });

  it('focuses no row when a Stack reopens the panel after a back', () => {
    const nav = openPicked(closePanel(back(pick({}, { book }, from))), { stack: 'Dune' });
    expect(nav.focusRow).toBeUndefined();
  });
});

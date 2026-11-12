import { describe, expect, it } from 'vitest';
import type { Book, Lane, Series } from '../contract/tierlist';
import type { Filters } from '../filter/filter';
import { laneEntries } from './lane';

const filters: Filters = { query: '', author: null, tag: null, year: null };

function book(title: string, extra: Partial<Book> = {}): Book {
  return {
    title,
    authors: [],
    series: null,
    seriesIndex: null,
    rating: null,
    tags: [],
    blurb: null,
    tier: null,
    dateRead: null,
    read: true,
    ...extra,
  };
}

/** A series whose positions own the given book ids. */
function series(...owned: string[]): Series {
  return {
    colour: '#336699',
    positions: owned.map((id, index) => ({ number: String(index + 1), book: id })),
    override: false,
  };
}

const books = {
  '1': book('One'),
  '2': book('Two'),
  '3': book('Dune One'),
  '4': book('Earthsea One'),
};
const seriesByName = { Dune: series('3'), Earthsea: series('4') };

function labels(lane: Lane, shown: Filters = filters): string[] {
  return laneEntries(lane, books, {}, seriesByName, shown).map((entry) =>
    entry.kind === 'stack' ? `stack:${entry.name}` : `card:${entry.id}`,
  );
}

describe('laneEntries', () => {
  it('keeps the Lane item order, interleaving Stacks and Cards', () => {
    const lane: Lane = {
      tier: 's',
      items: [{ stack: 'Dune' }, { card: '1' }, { stack: 'Earthsea' }, { card: '2' }],
    };

    expect(labels(lane)).toEqual(['stack:Dune', 'card:1', 'stack:Earthsea', 'card:2']);
  });

  it('drops filtered Stacks and Cards without reordering the rest', () => {
    const lane: Lane = {
      tier: 's',
      items: [{ stack: 'Dune' }, { card: '1' }, { stack: 'Earthsea' }, { card: '2' }],
    };

    expect(labels(lane, { ...filters, query: 'earthsea' })).toEqual(['stack:Earthsea']);
  });

  it('skips references the payload does not hold', () => {
    const lane: Lane = {
      tier: 's',
      items: [{ stack: 'Gone' }, { card: '99' }, { card: '1' }],
    };

    expect(labels(lane)).toEqual(['card:1']);
  });

  it('resolves each Stack and Card with its data and cover', () => {
    const lane: Lane = { tier: 's', items: [{ stack: 'Dune' }, { card: '1' }] };
    const cover = { src: 'data:image/webp;base64,', colour: '#123456' };

    const [stackEntry, cardEntry] = laneEntries(lane, books, { '1': cover }, seriesByName, filters);

    expect(stackEntry).toEqual({ kind: 'stack', name: 'Dune', series: seriesByName.Dune });
    expect(cardEntry).toEqual({ kind: 'card', id: '1', book: books['1'], cover });
  });
});

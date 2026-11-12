import { describe, expect, it } from 'vitest';
import type { Book, Cover, Series } from '../contract/tierlist';
import { frontOf, resolve, sheetsBehind } from './stack';

function book(title: string, read = true): Book {
  return {
    title,
    authors: [],
    series: 'Saga',
    seriesIndex: null,
    rating: null,
    tags: [],
    blurb: null,
    tier: null,
    dateRead: null,
    read,
  };
}

const cover: Cover = { src: 'data:image/webp;base64,', colour: '#123456' };

/** A series whose positions own the given book ids, `null` for a Placeholder. */
function series(...owned: (string | null)[]): Series {
  return {
    colour: '#336699',
    positions: owned.map((id, index) => ({ number: String(index + 1), book: id })),
    override: false,
  };
}

const books = { a: book('A'), b: book('B', false), c: book('C') };

describe('resolve', () => {
  it('pairs every position with its book and cover, Placeholders with neither', () => {
    const resolved = resolve(series(null, 'a', 'b'), books, { b: cover });

    expect(resolved.map(({ position }) => position.number)).toEqual(['1', '2', '3']);
    expect(resolved.map(({ book }) => book?.title)).toEqual([undefined, 'A', 'B']);
    expect(resolved.map(({ cover: found }) => found)).toEqual([undefined, undefined, cover]);
  });

  it('leaves a book id missing from the books undefined instead of throwing', () => {
    const [entry] = resolve(series('gone'), books, {});
    expect(entry?.book).toBeUndefined();
    expect(entry?.cover).toBeUndefined();
  });

  it('resolves an empty series to nothing', () => {
    expect(resolve(series(), books, {})).toEqual([]);
  });
});

describe('frontOf', () => {
  it('prefers the first owned book with a cover over earlier owned books', () => {
    const front = frontOf(resolve(series(null, 'a', 'b', 'c'), books, { b: cover, c: cover }));
    expect(front?.book?.title).toBe('B');
  });

  it('falls back to the first owned book when none has a cover', () => {
    expect(frontOf(resolve(series(null, 'c', 'a'), books, {}))?.book?.title).toBe('C');
  });

  it('falls back to the first position when nothing is owned', () => {
    const front = frontOf(resolve(series(null, null), books, {}));
    expect(front?.position.number).toBe('1');
    expect(front?.book).toBeUndefined();
  });

  it('has no front for an empty series', () => {
    expect(frontOf([])).toBeUndefined();
  });
});

describe('sheetsBehind', () => {
  it.each([
    [0, 0],
    [1, 0],
    [2, 1],
    [3, 2],
    [12, 2],
  ])('shows %i positions with %i sheets behind the front', (count, expected) => {
    const ids = Array.from({ length: count }, () => null);
    expect(sheetsBehind(resolve(series(...ids), books, {}))).toBe(expected);
  });
});

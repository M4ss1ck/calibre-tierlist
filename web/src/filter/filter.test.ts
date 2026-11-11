import { describe, expect, it } from 'vitest';
import type { Book } from '../contract/tierlist';
import type { Filters } from './filter';
import { filterOptions, hasReadYears, matchesBook, matchesSeries } from './filter';

function book(overrides: Partial<Book> = {}): Book {
  return {
    title: 'Book',
    authors: ['Author'],
    series: null,
    seriesIndex: null,
    rating: null,
    tags: [],
    blurb: null,
    tier: null,
    dateRead: null,
    read: true,
    ...overrides,
  };
}

const none: Filters = { query: '', author: null, tag: null, year: null };

describe('matchesBook', () => {
  it('matches everything with no filters, even an empty book', () => {
    expect(matchesBook(book({ title: '' }), none)).toBe(true);
  });

  it('trims and case-folds the query', () => {
    expect(matchesBook(book({ title: 'Dune' }), { ...none, query: '  DUNE ' })).toBe(true);
    expect(matchesBook(book({ title: 'Dune' }), { ...none, query: 'Foundation' })).toBe(false);
  });

  it('matches the query against title, any author, or the series name', () => {
    expect(matchesBook(book({ title: 'Dune' }), { ...none, query: 'dun' })).toBe(true);
    expect(matchesBook(book({ authors: ['Frank Herbert'] }), { ...none, query: 'herbert' })).toBe(true);
    expect(matchesBook(book({ series: 'Dune Chronicles' }), { ...none, query: 'chronicles' })).toBe(true);
    expect(matchesBook(book({ title: 'Dune' }), { ...none, query: 'herbert' })).toBe(false);
  });

  it('matches author and tag exactly', () => {
    const dune = book({ authors: ['Frank Herbert'], tags: ['Sci-Fi'] });
    expect(matchesBook(dune, { ...none, author: 'Frank Herbert' })).toBe(true);
    expect(matchesBook(dune, { ...none, author: 'Frank' })).toBe(false);
    expect(matchesBook(dune, { ...none, tag: 'Sci-Fi' })).toBe(true);
    expect(matchesBook(dune, { ...none, tag: 'sci-fi' })).toBe(false);
  });

  it('matches the year of the Read State date, and never a missing one', () => {
    const read = book({ dateRead: '2024-03-01' });
    expect(matchesBook(read, { ...none, year: 2024 })).toBe(true);
    expect(matchesBook(read, { ...none, year: 2023 })).toBe(false);
    expect(matchesBook(book({ read: true }), { ...none, year: 2024 })).toBe(false);
  });

  it('requires every set criterion (AND)', () => {
    const dune = book({ title: 'Dune', authors: ['Frank Herbert'], tags: ['Sci-Fi'], dateRead: '2024-03-01' });
    expect(matchesBook(dune, { query: 'dune', author: 'Frank Herbert', tag: 'Sci-Fi', year: 2024 })).toBe(true);
    expect(matchesBook(dune, { ...none, author: 'Frank Herbert', tag: 'Fantasy' })).toBe(false);
  });
});

describe('matchesSeries', () => {
  const books = [book({ title: 'Dune', series: 'Dune Chronicles', tags: ['Sci-Fi'] })];

  it('matches when any of its books matches', () => {
    expect(matchesSeries('Dune Chronicles', books, { ...none, query: 'dune' })).toBe(true);
  });

  it('matches on the series name plus a book criterion', () => {
    expect(matchesSeries('Dune Chronicles', books, { ...none, query: 'chronicles', tag: 'Sci-Fi' })).toBe(true);
    expect(matchesSeries('Dune Chronicles', books, { ...none, query: 'chronicles', tag: 'Fantasy' })).toBe(false);
    expect(matchesSeries('Foundation', books, { ...none, query: 'asimov' })).toBe(false);
  });
});

describe('filterOptions', () => {
  it('lists sorted unique authors, tags and years (newest first)', () => {
    const books = [
      book({ authors: ['Zed', 'Amy'], tags: ['b', 'a'], dateRead: '2021-01-01' }),
      book({ authors: ['Amy'], tags: ['a', 'c'], dateRead: '2024-06-01' }),
      book({ authors: [], tags: [] }),
    ];
    expect(filterOptions(books)).toEqual({
      authors: ['Amy', 'Zed'],
      tags: ['a', 'b', 'c'],
      years: [2024, 2021],
    });
    expect(filterOptions([])).toEqual({ authors: [], tags: [], years: [] });
  });
});

describe('hasReadYears', () => {
  it('is true only when a book has a Read State date', () => {
    expect(hasReadYears([book(), book({ read: true })])).toBe(false);
    expect(hasReadYears([book(), book({ dateRead: '2024-03-01' })])).toBe(true);
  });
});

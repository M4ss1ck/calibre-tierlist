import type { Book } from '../contract/tierlist';

export interface Filters {
  query: string;
  author: string | null;
  tag: string | null;
  year: number | null;
}

export interface FilterOptions {
  authors: string[];
  tags: string[];
  years: number[];
}

/** The year of a book's Read State date, or null when it has none. */
function readYear(dateRead: string | null): number | null {
  if (dateRead === null) return null;
  const year = Number.parseInt(dateRead.slice(0, 4), 10);
  return Number.isNaN(year) ? null : year;
}

function includes(text: string, query: string): boolean {
  return text.toLowerCase().includes(query);
}

/** Author, tag and year criteria; the query is not considered. */
function criteriaHold(book: Book, filters: Filters): boolean {
  if (filters.author !== null && !book.authors.includes(filters.author)) return false;
  if (filters.tag !== null && !book.tags.includes(filters.tag)) return false;
  if (filters.year !== null && readYear(book.dateRead) !== filters.year) return false;
  return true;
}

function queryMatches(book: Book, query: string): boolean {
  if (query === '') return true;
  if (includes(book.title, query)) return true;
  if (book.authors.some((author) => includes(author, query))) return true;
  return book.series !== null && includes(book.series, query);
}

/** True when the book satisfies every set criterion (AND). */
export function matchesBook(book: Book, filters: Filters): boolean {
  return criteriaHold(book, filters) && queryMatches(book, filters.query.trim().toLowerCase());
}

/**
 * A Stack stays visible if anything in it matches: its series name answers the
 * query and its books answer the other criteria, or one of its books matches.
 */
export function matchesSeries(name: string, books: readonly Book[], filters: Filters): boolean {
  if (books.some((book) => matchesBook(book, filters))) return true;
  const query = filters.query.trim().toLowerCase();
  if (query !== '' && !includes(name, query)) return false;
  return books.some((book) => criteriaHold(book, filters));
}

/** Sorted unique authors and tags, and years (newest first), present in the data. */
export function filterOptions(books: readonly Book[]): FilterOptions {
  const authors = new Set<string>();
  const tags = new Set<string>();
  const years = new Set<number>();
  for (const book of books) {
    for (const author of book.authors) authors.add(author);
    for (const tag of book.tags) tags.add(tag);
    const year = readYear(book.dateRead);
    if (year !== null) years.add(year);
  }
  return {
    authors: [...authors].sort((a, b) => a.localeCompare(b)),
    tags: [...tags].sort((a, b) => a.localeCompare(b)),
    years: [...years].sort((a, b) => b - a),
  };
}

/** False when no book has a Read State date, so the UI can hide the year filter. */
export function hasReadYears(books: readonly Book[]): boolean {
  return books.some((book) => readYear(book.dateRead) !== null);
}

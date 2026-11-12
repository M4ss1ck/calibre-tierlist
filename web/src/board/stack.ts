import type { Book, Cover, Position, Series } from '../contract/tierlist';

/** What a Stack asks the board to open: its series panel. */
export type StackPick = { stack: string };

/** One Stack position resolved against the board's books and covers. */
export type Resolved = { position: Position; book: Book | undefined; cover: Cover | undefined };

/** Every position of a series with its owned book and cover, in index order. */
export function resolve(
  series: Series,
  books: Record<string, Book>,
  covers: Record<string, Cover>,
): Resolved[] {
  return series.positions.map((position) => ({
    position,
    book: position.book === null ? undefined : books[position.book],
    cover: position.book === null ? undefined : covers[position.book],
  }));
}

/** Whether this position can be a Series Cover: an owned book with a cover. */
export function canFront(entry: Resolved): boolean {
  return entry.book !== undefined && entry.cover !== undefined;
}

/**
 * The position a Stack shows in front, its Series Cover: the book id `chosen`
 * names when it is one that can front, else the first owned book with a cover,
 * else the first owned book, else the first position.
 */
export function frontOf(resolved: Resolved[], chosen?: string): Resolved | undefined {
  return (
    resolved.find((entry) => chosen !== undefined && entry.position.book === chosen && canFront(entry)) ??
    resolved.find(canFront) ??
    resolved.find((entry) => entry.book) ??
    resolved[0]
  );
}

/**
 * The pick a click on `book`'s eye leaves: clicking the book already in front
 * returns the series to its default Series Cover, any other book becomes it.
 */
export function pickFront(resolved: Resolved[], chosen: string | undefined, book: string): string | undefined {
  return frontOf(resolved, chosen)?.position.book === book ? undefined : book;
}

/** How many of the series' books in the library are read, out of how many are in it. */
export function readCount(resolved: Resolved[]): { read: number; total: number } {
  const owned = resolved.filter((entry) => entry.book !== undefined);
  return { read: owned.filter((entry) => entry.book?.read === true).length, total: owned.length };
}

/** The session's Series Cover picks with `name`'s set to `chosen`, or dropped when `chosen` is undefined. */
export function withFront(fronts: Record<string, string>, name: string, chosen: string | undefined) {
  const rest = Object.fromEntries(Object.entries(fronts).filter(([series]) => series !== name));
  return chosen === undefined ? rest : { ...rest, [name]: chosen };
}

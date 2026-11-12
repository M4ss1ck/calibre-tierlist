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

/**
 * The position a collapsed Stack shows in front: the first owned book with a
 * cover, else the first owned book, else the first position.
 */
export function frontOf(resolved: Resolved[]): Resolved | undefined {
  return (
    resolved.find((entry) => entry.book && entry.cover) ??
    resolved.find((entry) => entry.book) ??
    resolved[0]
  );
}

/** How many of the series' books in the library are read, out of how many are in it. */
export function readCount(resolved: Resolved[]): { read: number; total: number } {
  const owned = resolved.filter((entry) => entry.book !== undefined);
  return { read: owned.filter((entry) => entry.book?.read === true).length, total: owned.length };
}

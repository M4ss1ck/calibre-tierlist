import type { Book, Cover, Position, Series } from '../contract/tierlist';

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

/** How many sheets peek out behind the front: one per other position, at most two. */
export function sheetsBehind(resolved: Resolved[]): number {
  return Math.min(2, Math.max(0, resolved.length - 1));
}

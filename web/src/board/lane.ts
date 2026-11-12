import type { Book, Cover, Lane, Series } from '../contract/tierlist';
import type { Filters } from '../filter/filter';
import { matchesBook, matchesSeries } from '../filter/filter';

/** One thing a Lane draws, in Lane Order: a Stack or a Card. */
export type LaneEntry =
  | { kind: 'stack'; name: string; series: Series }
  | { kind: 'card'; id: string; book: Book; cover: Cover | undefined };

/**
 * The Lane's items that survive the Board Filter, in Lane Order. Stacks and
 * Cards stay interleaved as the payload orders them; references the payload
 * does not hold are skipped.
 */
export function laneEntries(
  lane: Lane,
  books: Record<string, Book>,
  covers: Record<string, Cover>,
  series: Record<string, Series>,
  filters: Filters,
): LaneEntry[] {
  return lane.items.flatMap((item): LaneEntry[] => {
    if ('stack' in item) {
      const entry = series[item.stack];
      if (!entry) return [];
      const owned = entry.positions.flatMap((position) => {
        const book = position.book === null ? undefined : books[position.book];
        return book ? [book] : [];
      });
      return matchesSeries(item.stack, owned, filters) ? [{ kind: 'stack', name: item.stack, series: entry }] : [];
    }
    const book = books[item.card];
    return book && matchesBook(book, filters) ? [{ kind: 'card', id: item.card, book, cover: covers[item.card] }] : [];
  });
}

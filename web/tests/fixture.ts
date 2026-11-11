import type { Book, TierListData } from '../src/contract/tierlist';
import { loadFixture } from './page';

/**
 * The shared fixture with 40 Cards per Lane: tall enough that the board spills
 * over one A4 page, and large enough to exceed `SAFE_LIMITS` at scale 2.
 */
export async function oversized(): Promise<TierListData> {
  const base = await loadFixture();
  const books: Record<string, Book> = {};
  const lanes = base.lanes.map((lane) => {
    if (lane.tier === null) return { ...lane, cards: [], stacks: [] };
    const tier: string = lane.tier;
    const cards = Array.from({ length: 40 }, (_, index) => {
      const id = `${tier}-${index}`;
      books[id] = {
        title: `${tier.toUpperCase()} book ${index + 1}`,
        authors: [],
        series: null,
        seriesIndex: null,
        rating: null,
        tags: [],
        blurb: null,
        tier,
        dateRead: null,
        read: true,
      };
      return id;
    });
    return { tier, cards, stacks: [] };
  });

  return { ...base, lanes, books, series: {}, covers: {} };
}

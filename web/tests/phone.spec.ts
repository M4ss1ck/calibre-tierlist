import { expect, test, type Page } from '@playwright/test';
import type { Book, Position, TierListData } from '../src/contract/tierlist';
import { fixtureBoardUrl, loadFixture } from './page';

let url: string;

const phone = { width: 375, height: 812 };
test.use({ viewport: phone });

const longTitle = 'A Title That Goes On And On Without Ever Stopping At All';
const longWord = 'Supercalifragilisticexpialidocious';
const seriesName = 'The Antidisestablishmentarianism Cycle';

/** One Book with the longest strings the layout has to survive. */
function book(title: string, extra: Partial<Book> = {}): Book {
  return {
    title,
    authors: ['A Writer With A Rather Long Name'],
    series: null,
    seriesIndex: null,
    rating: null,
    tags: ['an-unreasonably-long-tag'],
    blurb: `${longWord} ${longWord} ${longWord}`,
    tier: 's',
    dateRead: null,
    read: false,
    ...extra,
  };
}

/** The fixture crowded with long titles and a long Stack, so the phone layout has to cope. */
function crowded(base: TierListData): TierListData {
  const books: Record<string, Book> = { ...base.books };
  const cards: string[] = [];

  for (let index = 1; index <= 12; index += 1) {
    const id = `phone-${index}`;
    cards.push(id);
    books[id] = book(`${longTitle} ${index}`);
  }

  const owned = 'phone-series-1';
  books[owned] = book(`${longWord} ${longWord}`, { series: seriesName, seriesIndex: '1', tier: 'b' });

  const positions: Position[] = Array.from({ length: 6 }, (_, index) => ({
    number: String(index + 1),
    book: index === 0 ? owned : null,
  }));

  return {
    ...base,
    books,
    lanes: base.lanes.map((lane) =>
      lane.tier === 's'
        ? {
            ...lane,
            items: [...lane.items, ...cards.map((card) => ({ card })), { stack: seriesName }],
          }
        : lane,
    ),
    series: {
      ...base.series,
      [seriesName]: { colour: '#336699', positions, override: false },
    },
  };
}

/** A phone has no room for a sideways scroll: nothing may stick out of the viewport. */
async function expectNoSideScroll(page: Page) {
  await expect
    .poll(() =>
      page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
      ),
    )
    .toBeLessThanOrEqual(0);
}

test.beforeAll(async () => {
  url = await fixtureBoardUrl(crowded(await loadFixture()));
});

test('fits the whole board without sideways scroll', async ({ page }) => {
  await page.goto(url);

  await expect(page.getByText(`${longTitle} 1`, { exact: true })).toBeVisible();
  await expect(page.getByRole('region', { name: 'Unranked' })).toBeVisible();
  await expectNoSideScroll(page);
});

test('fits the series panel of a long series with every position listed', async ({ page }) => {
  await page.goto(url);

  await page.getByRole('figure', { name: seriesName }).getByRole('button').click();
  const panel = page.getByRole('dialog', { name: seriesName });
  await expect(panel).toBeVisible();
  await expect(panel.getByRole('listitem')).toHaveCount(6);

  const box = await panel.boundingBox();
  if (!box) throw new Error('Series panel has no box');
  expect(box.x).toBeGreaterThanOrEqual(0);
  expect(box.x + box.width).toBeLessThanOrEqual(phone.width);
  await expectNoSideScroll(page);
});

test('fits the detail panel with its longest book', async ({ page }) => {
  await page.goto(url);

  const card = page
    .getByRole('article')
    .filter({ has: page.getByText(`${longTitle} 1`, { exact: true }) });
  await card.getByRole('button').click();
  const panel = page.getByRole('dialog', { name: `${longTitle} 1` });
  await expect(panel).toBeVisible();
  await expect(panel.locator('.blurb')).toContainText(longWord);

  const box = await panel.boundingBox();
  if (!box) throw new Error('Detail panel has no box');
  expect(box.x).toBeGreaterThanOrEqual(0);
  expect(box.x + box.width).toBeLessThanOrEqual(phone.width);
  await expectNoSideScroll(page);
});

import { expect, test } from '@playwright/test';
import type { TierListData } from '../src/contract/tierlist';
import { fixtureBoardUrl, loadFixture } from './page';

let data: TierListData;
let url: string;

test.beforeAll(async () => {
  data = await loadFixture();
  url = await fixtureBoardUrl();
});

function titles(ids: string[]): string[] {
  return ids.map((id) => {
    const book = data.books[id];
    if (!book) {
      throw new Error(`Fixture Lane references unknown book id ${id}`);
    }
    return book.title;
  });
}

function onBoard(): string[] {
  return data.lanes.flatMap((lane) => lane.cards);
}

test('shows one Lane per Tier in config order, then the Unranked Lane', async ({ page }) => {
  await page.goto(url);

  const labels = await page
    .locator('section')
    .evaluateAll((sections) => sections.map((section) => section.getAttribute('aria-label')));

  expect(labels).toEqual([...data.tiers.map((tier) => tier.label), 'Unranked']);
});

test('shows each Lane its own Card titles in order', async ({ page }) => {
  await page.goto(url);

  const sections = page.locator('section');
  await expect(sections).toHaveCount(data.lanes.length);

  for (const [index, lane] of data.lanes.entries()) {
    const expected = titles(lane.cards);
    const cards = sections.nth(index).locator('article');

    await expect(cards).toHaveCount(expected.length);
    if (expected.length > 0) {
      await expect(cards.locator('.title')).toHaveText(expected);
    }
  }
});

test('shows every book with a cover its embedded image', async ({ page }) => {
  await page.goto(url);

  const withCovers = onBoard().filter((id) => id in data.covers);
  expect(withCovers.length).toBeGreaterThan(0);
  await expect(page.locator('article img')).toHaveCount(withCovers.length);

  for (const id of withCovers) {
    const cover = data.covers[id];
    const book = data.books[id];
    if (!cover || !book) {
      throw new Error(`Fixture is missing the cover or book for ${id}`);
    }

    const image = page
      .locator('article')
      .filter({ has: page.locator('.title', { hasText: book.title }) })
      .locator('img');

    await expect(image).toHaveCount(1);
    await expect(image).toHaveAttribute('src', cover.src);
    await expect
      .poll(() => image.evaluate((element) => (element as HTMLImageElement).naturalWidth))
      .toBeGreaterThan(0);
  }
});

test('draws the Placeholder style for every book without a cover', async ({ page }) => {
  await page.goto(url);

  const withoutCovers = onBoard().filter((id) => !(id in data.covers));
  expect(withoutCovers.length).toBeGreaterThan(0);

  for (const id of withoutCovers) {
    const book = data.books[id];
    if (!book) {
      throw new Error(`Fixture Lane references unknown book id ${id}`);
    }

    const card = page
      .locator('article')
      .filter({ has: page.locator('.title', { hasText: book.title }) });

    await expect(card).toHaveCount(1);
    await expect(card).toHaveClass(/\bplaceholder\b/);
    await expect(card).toContainText('no cover');
    await expect(card.locator('img')).toHaveCount(0);
  }
});

test('shows a title containing script markup and logs no page errors', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (error) => errors.push(error.message));

  await page.goto(url);

  await expect(page.getByText('The </script> Problem', { exact: true })).toBeVisible();
  expect(errors).toEqual([]);
});

test('loads without any network request beyond the document itself', async ({ page }) => {
  const requests: string[] = [];
  page.on('request', (request) => requests.push(request.url()));

  await page.goto(url);
  await expect(page.locator('article').first()).toBeVisible();

  expect(requests).toEqual([url]);
});

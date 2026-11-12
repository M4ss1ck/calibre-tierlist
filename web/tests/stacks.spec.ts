import { expect, test, type Page } from '@playwright/test';
import type { Series, TierListData } from '../src/contract/tierlist';
import { fixtureBoardUrl, loadFixture } from './page';

let data: TierListData;
let url: string;

test.beforeAll(async () => {
  data = await loadFixture();
  url = await fixtureBoardUrl();
});

function seriesOf(name: string): Series {
  const series = data.series[name];
  if (!series) throw new Error(`Fixture has no series ${name}`);
  return series;
}

/** Every Stack the fixture places on the board, with the Lane index that names it. */
function placed(): { name: string; lane: number }[] {
  return data.lanes.flatMap((lane, index) =>
    lane.items.flatMap((item) =>
      'stack' in item && item.stack in data.series ? [{ name: item.stack, lane: index }] : [],
    ),
  );
}

const owned = (name: string) => seriesOf(name).positions.filter((position) => position.book !== null);
const stack = (page: Page, name: string) => page.getByRole('figure', { name, exact: true });

/** How many of the series' books in the library are read, out of how many are in it. */
function readCount(name: string): { read: number; total: number } {
  const books = owned(name).flatMap(({ book }) => (book === null ? [] : [data.books[book]]));
  return { read: books.filter((book) => book?.read === true).length, total: books.length };
}

test('draws each Stack once, in the Lane that names it', async ({ page }) => {
  await page.goto(url);
  expect(placed().length).toBeGreaterThan(1);

  for (const { name, lane } of placed()) {
    await expect(stack(page, name)).toHaveCount(1);
    await expect(page.locator('section').nth(lane).getByRole('figure', { name, exact: true })).toHaveCount(1);
  }
});

test('shows the cover of the first owned book that has one in front', async ({ page }) => {
  await page.goto(url);
  let fronted = 0;

  for (const { name } of placed()) {
    const first = owned(name).find((position) => position.book !== null && position.book in data.covers);
    const image = stack(page, name).locator('.front img.cover');
    if (first?.book) {
      await expect(image).toHaveCount(1);
      await expect(image).toHaveAttribute('src', data.covers[first.book]?.src ?? '');
      fronted += 1;
    } else {
      await expect(image).toHaveCount(0);
    }
  }

  expect(fronted).toBeGreaterThan(0);
});

test('fills a Stack with no cover with its series colour and leaves an unread front undimmed', async ({ page }) => {
  await page.goto(url);
  const bare = placed().find(({ name }) => owned(name).every(({ book }) => book === null || !(book in data.covers)));
  if (!bare) throw new Error('Fixture has no Stack without covers');
  const front = owned(bare.name)[0]?.book;
  if (!front || data.books[front]?.read !== false) throw new Error('Fixture bare Stack should front an unread book');

  const button = stack(page, bare.name).locator('.front');
  await expect(button).toHaveCSS('background-image', /linear-gradient/);
  await expect(button).toHaveCSS('filter', 'none');
  await expect(button).toHaveCSS('opacity', '1');
});

test('counts the read books over the books in the library, Placeholders left out', async ({ page }) => {
  await page.goto(url);

  for (const { name } of placed()) {
    const { read, total } = readCount(name);
    await expect(stack(page, name).locator('.count')).toHaveText(`${read}/${total}`);
  }
});

test('names the series in a box and in the button that opens it', async ({ page }) => {
  await page.goto(url);

  for (const { name } of placed()) {
    const { read, total } = readCount(name);
    await expect(stack(page, name).locator('.name')).toHaveText(name);
    await expect(
      stack(page, name).getByRole('button', { name: `${name}, ${read} of ${total} read` }),
    ).toBeVisible();
  }
});

test('draws no sheets behind a Stack and never dims its front', async ({ page }) => {
  await page.goto(`${url}?sheets=1`);

  await expect(page.locator('.behind')).toHaveCount(0);
  const covers = page.locator('figure.stack .cover');
  expect(await covers.count()).toBeGreaterThan(0);
  for (const cover of await covers.all()) {
    await expect(cover).toHaveCSS('filter', 'none');
    await expect(cover).toHaveCSS('opacity', '1');
  }
});

test('draws no per-position elements, Tier badges or "+N" badge', async ({ page }) => {
  await page.goto(url);

  for (const selector of ['.position', '.tier-badge', '.more', 'button.toggle']) {
    await expect(page.locator(`figure.stack ${selector}`)).toHaveCount(0);
  }
  for (const { name } of placed()) {
    await expect(stack(page, name).getByRole('button')).toHaveCount(1);
  }
});

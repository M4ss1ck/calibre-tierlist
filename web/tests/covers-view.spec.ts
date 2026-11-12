import { expect, test, type Page } from '@playwright/test';
import type { Book, Series, TierListData } from '../src/contract/tierlist';
import { fixtureBoardUrl, loadFixture } from './page';

let data: TierListData;
let url: string;

test.beforeAll(async () => {
  data = await loadFixture();
  url = await fixtureBoardUrl();
});

const stack = (page: Page, name: string) => page.getByRole('figure', { name, exact: true });

/** The series' books in the library, with how many of them are read. */
function readCount(name: string): { read: number; total: number } {
  const series: Series | undefined = data.series[name];
  if (!series) throw new Error(`Fixture has no series ${name}`);
  const owned = series.positions.flatMap((position) => {
    const book: Book | undefined = position.book === null ? undefined : data.books[position.book];
    return book ? [book] : [];
  });
  return { read: owned.filter((book) => book.read).length, total: owned.length };
}

/** Open the View Panel, change one control and close it again. */
async function change(page: Page, name: string) {
  await page.getByRole('button', { name: 'Customize view' }).click();
  await page.getByRole('dialog', { name: 'Customize view' }).getByRole('switch', { name }).click();
  await page.keyboard.press('Escape');
}

test('shows how many of a series read books are read, in the badge and the button name', async ({ page }) => {
  await page.goto(url);

  const counts = readCount('Dune');
  expect(`${counts.read}/${counts.total}`).toBe('2/3');
  await expect(stack(page, 'Dune').locator('.count')).toHaveText('2/3');
  await expect(stack(page, 'Dune').getByRole('button', { name: 'Dune, 2 of 3 read' })).toBeVisible();
  await expect(stack(page, 'Earthsea').locator('.count')).toHaveText('0/1');
});

test('hides the Read Count from the panel', async ({ page }) => {
  await page.goto(url);
  await change(page, 'Read count');

  await expect(page.locator('.count')).toHaveCount(0);
  await expect(stack(page, 'Dune').getByRole('button', { name: 'Dune, 2 of 3 read' })).toBeVisible();
});

test('hides every Caption from the panel', async ({ page }) => {
  await page.goto(url);
  await expect(page.locator('article .title').first()).toBeVisible();
  await expect(stack(page, 'Dune').locator('.name')).toHaveText('Dune');

  await change(page, 'Captions');

  await expect(page.locator('article .title')).toHaveCount(0);
  await expect(page.locator('figure .name')).toHaveCount(0);
});

test('draws Cards 1.25 times wider at ?cover_size=large', async ({ page }) => {
  const width = () => page.locator('article.card').first().evaluate((card) => card.getBoundingClientRect().width);

  await page.goto(url);
  const normal = await width();
  await page.goto(`${url}?cover_size=large`);

  expect(await width()).toBeCloseTo(normal * 1.25, 1);
});

test('closes the Cover Gap up at ?cover_gap=none', async ({ page }) => {
  await page.goto(`${url}?cover_gap=none`);
  await expect(page.locator('.cards').first()).toHaveCSS('column-gap', '0px');
});

test('keeps the Cover Gap on a phone, capped at the phone spacing', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto(`${url}?cover_gap=none`);
  await expect(page.locator('.cards').first()).toHaveCSS('column-gap', '0px');
  await page.goto(url);
  await expect(page.locator('.cards').first()).toHaveCSS('column-gap', '12px');
});

import { expect, test, type Page } from '@playwright/test';
import type { Series, TierListData } from '../src/contract/tierlist';
import { fixtureBoardUrl, loadFixture } from './page';

let data: TierListData;
let url: string;

test.beforeAll(async () => {
  data = await loadFixture();
  url = await fixtureBoardUrl();
});

/** The fixture series whose Stack cuts positions: the panel must list those too. */
function cut(): [string, Series] {
  const found = Object.entries(data.series).find(([, series]) => series.more > 0);
  if (!found) throw new Error('Fixture has no Stack with cut positions');
  return found;
}

const ownedCount = (series: Series) => series.positions.filter((position) => position.book !== null).length;

/** Click the Stack named `name` and return its series panel. */
async function openPanel(page: Page, name: string, series: Series) {
  const opener = page.getByRole('button', {
    name: `${name}, ${ownedCount(series)} of ${series.positions.length} books`,
  });
  await opener.click();
  const panel = page.getByRole('dialog', { name });
  await expect(panel).toBeVisible();
  return { opener, panel, rows: panel.getByRole('listitem') };
}

test('lists every position of the series, cut ones included, in order', async ({ page }) => {
  const [name, series] = cut();
  await page.goto(url);
  const { panel, rows } = await openPanel(page, name, series);

  await expect(panel.locator('.summary')).toHaveText(
    `${ownedCount(series)} of ${series.positions.length} books in your library`,
  );
  await expect(rows).toHaveCount(series.positions.length);
  await expect(rows.locator('.number')).toHaveText(series.positions.map(({ number }) => `#${number}`));
});

test('says "Not in your library" for each Placeholder and shows owned books with their Tier', async ({
  page,
}) => {
  const [name, series] = cut();
  await page.goto(url);
  const { rows } = await openPanel(page, name, series);

  for (const [index, position] of series.positions.entries()) {
    const row = rows.nth(index);
    if (position.book === null) {
      await expect(row.locator('.title')).toHaveText('Not in your library');
      await expect(row.locator('.tier')).toHaveCount(0);
      continue;
    }
    const book = data.books[position.book];
    const tier = data.tiers.find((candidate) => candidate.id === book?.tier);
    await expect(row.locator('.title')).toHaveText(book?.title ?? '');
    await expect(row.locator('.tier')).toHaveText(tier?.label ?? 'Unranked');
  }
});

test('opens the Detail panel for an owned book picked from the list', async ({ page }) => {
  const [name, series] = cut();
  const id = series.positions.find((position) => position.book !== null)?.book;
  const book = id ? data.books[id] : undefined;
  if (!book) throw new Error('Fixture cut Stack should own a book');
  await page.goto(url);
  const { panel, rows } = await openPanel(page, name, series);

  await rows.filter({ hasText: book.title }).getByRole('button').click();
  await expect(panel).toBeHidden();
  await expect(page.getByRole('dialog', { name: book.title })).toBeVisible();
});

test('opens the Detail panel for a cut Placeholder picked from the list', async ({ page }) => {
  const [name, series] = cut();
  const last = series.positions.at(-1);
  if (!last || last.book !== null) throw new Error('Fixture cut Stack should end in a Placeholder');
  await page.goto(url);
  const { rows } = await openPanel(page, name, series);

  await rows.last().getByRole('button').click();
  const detail = page.getByRole('dialog', { name: `${name} #${last.number}` });
  await expect(detail).toBeVisible();
  await expect(detail.locator('.library')).toHaveText('Not in your library');
});

test('closes on Escape and on its close button, returning focus to the Stack', async ({ page }) => {
  const [name, series] = cut();
  await page.goto(url);

  const first = await openPanel(page, name, series);
  await page.keyboard.press('Escape');
  await expect(first.panel).toBeHidden();
  await expect(first.opener).toBeFocused();

  const second = await openPanel(page, name, series);
  await second.panel.getByRole('button', { name: 'Close' }).click();
  await expect(second.panel).toBeHidden();
  await expect(second.opener).toBeFocused();
});

test('lists the one position of a single-book series', async ({ page }) => {
  const single = Object.entries(data.series).find(([, series]) => series.positions.length === 1);
  if (!single) throw new Error('Fixture has no single-position Stack');
  await page.goto(url);

  const { rows } = await openPanel(page, ...single);
  await expect(rows).toHaveCount(1);
});

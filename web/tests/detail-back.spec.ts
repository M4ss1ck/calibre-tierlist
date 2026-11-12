import { expect, test, type Page } from '@playwright/test';
import type { TierListData } from '../src/contract/tierlist';
import { fixtureBoardUrl, loadFixture } from './page';

let data: TierListData;
let url: string;

test.beforeAll(async () => {
  data = await loadFixture();
  url = await fixtureBoardUrl();
});

const duneStack = (page: Page) => page.getByRole('figure', { name: 'Dune', exact: true }).getByRole('button');
const panel = (page: Page) => page.getByRole('dialog', { name: 'Dune' });
const back = (page: Page) => page.getByRole('button', { name: 'Back to Dune' });

/** Dune's third row and its title: an owned book after a Placeholder, so the focus check means something. */
function thirdRow() {
  const position = data.series['Dune']?.positions[2];
  const title = position?.book ? data.books[position.book]?.title : undefined;
  if (!title) throw new Error("Fixture Dune's third position should be an owned book");
  return title;
}

async function openThirdFromDune(page: Page) {
  const title = thirdRow();
  await page.goto(url);
  await duneStack(page).click();
  await panel(page).getByRole('listitem').nth(2).locator('button.title').click();
  const detail = page.getByRole('dialog', { name: title });
  await expect(detail).toBeVisible();
  return { title, detail };
}

test('goes back from Detail to the series list, focused on the row that opened it', async ({ page }) => {
  const { title, detail } = await openThirdFromDune(page);

  await expect(back(page)).toHaveAttribute('title', 'Back to Dune');
  await back(page).click();

  await expect(detail).toBeHidden();
  await expect(panel(page)).toBeVisible();
  await expect(panel(page).getByRole('button', { name: title, exact: true })).toBeFocused();
});

test('keeps a Series Cover pick across the trip to Detail and back', async ({ page }) => {
  const id = data.series['Dune']?.positions[3]?.book;
  if (!id) throw new Error("Fixture Dune's fourth position should be an owned book");
  await page.goto(url);
  await duneStack(page).click();
  const eye = () => panel(page).getByRole('listitem').nth(3).getByRole('button', { name: 'Use this cover for the series' });
  await eye().click();

  await panel(page).getByRole('listitem').nth(3).locator('button.title').click();
  await back(page).click();

  await expect(eye()).toHaveAttribute('aria-pressed', 'true');
});

test('closes everything on the close button and on Escape, as before', async ({ page }) => {
  const first = await openThirdFromDune(page);
  await first.detail.getByRole('button', { name: 'Close' }).click();
  await expect(first.detail).toBeHidden();
  await expect(panel(page)).toBeHidden();

  const second = await openThirdFromDune(page);
  await page.keyboard.press('Escape');
  await expect(second.detail).toBeHidden();
  await expect(panel(page)).toBeHidden();
});

test('closing the list reached by back returns focus to the Stack', async ({ page }) => {
  await openThirdFromDune(page);
  await back(page).click();

  await page.keyboard.press('Escape');

  await expect(panel(page)).toBeHidden();
  await expect(duneStack(page)).toBeFocused();
});

test('shows no back button on Detail opened from a standalone Card', async ({ page }) => {
  const book = data.books['1'];
  if (!book) throw new Error('Fixture has no book 1');
  await page.goto(url);

  await page.getByRole('button', { name: book.title }).click();

  await expect(page.getByRole('dialog', { name: book.title })).toBeVisible();
  await expect(page.getByRole('button', { name: /^Back to / })).toHaveCount(0);
});

test('shows no back button after a Card, even right after a trip through a series', async ({ page }) => {
  const book = data.books['1'];
  if (!book) throw new Error('Fixture has no book 1');
  const { detail } = await openThirdFromDune(page);
  await detail.getByRole('button', { name: 'Close' }).click();

  await page.getByRole('button', { name: book.title }).click();

  await expect(page.getByRole('button', { name: /^Back to / })).toHaveCount(0);
});

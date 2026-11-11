import { expect, test } from '@playwright/test';
import type { TierListData } from '../src/contract/tierlist';
import { fixtureBoardUrl, loadFixture } from './page';

let data: TierListData;
let url: string;

test.beforeAll(async () => {
  data = await loadFixture();
  url = await fixtureBoardUrl();
});

function bookOf(id: string) {
  const book = data.books[id];
  if (!book) throw new Error(`Fixture has no book ${id}`);
  return book;
}

test('opens a book Card in a detail panel with everything known about it', async ({ page }) => {
  const book = bookOf('1');
  const tier = data.tiers.find((candidate) => candidate.id === book.tier);
  await page.goto(url);

  await page.getByRole('button', { name: book.title }).click();
  const panel = page.getByRole('dialog', { name: book.title });
  await expect(panel).toBeVisible();
  await expect(panel.locator('.authors')).toHaveText(book.authors.join(', '));
  await expect(panel.locator('.tier')).toHaveText(tier?.label ?? '');
  await expect(panel.locator('.read')).toHaveText(book.dateRead ?? '');
  await expect(panel.locator('.rating')).toHaveText(`${book.rating} / 5`);
  await expect(panel.locator('.tags')).toHaveText(book.tags.join(', '));
  await expect(panel.locator('.blurb')).toHaveText(book.blurb ?? '');
  await expect(panel.locator('.series')).toHaveCount(0);
});

test('shows a Stack book with its series and omits what it lacks', async ({ page }) => {
  const book = bookOf('3');
  await page.goto(url);

  await page.getByRole('figure', { name: 'Dune' }).getByRole('button', { name: book.title }).click();
  const panel = page.getByRole('dialog', { name: book.title });
  await expect(panel.locator('.series')).toHaveText(`Dune #${book.seriesIndex}`);
  for (const missing of ['.rating', '.tags', '.blurb', '.status']) {
    await expect(panel.locator(missing)).toHaveCount(0);
  }
});

test('opens a Placeholder with its series, number and that it is not owned', async ({ page }) => {
  await page.goto(url);

  await page.getByRole('button', { name: 'Dune #1, not in your library' }).click();
  const panel = page.getByRole('dialog', { name: 'Dune #1' });
  await expect(panel.locator('.series')).toHaveText('Dune #1');
  await expect(panel.locator('.status')).toHaveText('Not in your library');
  await expect(panel.locator('.tier')).toHaveCount(0);
  await expect(panel.locator('.read')).toHaveCount(0);
});

test('opens from the keyboard, closes on Escape and returns focus', async ({ page }) => {
  const title = bookOf('1').title;
  await page.goto(url);

  const card = page.getByRole('button', { name: title });
  await card.focus();
  await page.keyboard.press('Enter');
  const panel = page.getByRole('dialog', { name: title });
  await expect(panel).toBeVisible();

  await page.keyboard.press('Escape');
  await expect(panel).toBeHidden();
  await expect(card).toBeFocused();
});

test('closes with the close button and returns focus', async ({ page }) => {
  await page.goto(url);

  const placeholder = page.getByRole('button', { name: 'Dune #1, not in your library' });
  await placeholder.focus();
  await page.keyboard.press('Space');
  await page.getByRole('dialog').getByRole('button', { name: 'Close' }).click();
  await expect(page.getByRole('dialog')).toBeHidden();
  await expect(placeholder).toBeFocused();
});

import { expect, test } from '@playwright/test';
import type { Book, TierListData } from '../src/contract/tierlist';
import { fixtureBoardUrl, loadFixture } from './page';

let data: TierListData;
let url: string;

test.beforeAll(async () => {
  data = await loadFixture();
  url = await fixtureBoardUrl();
});

/** The same books with every Read State date removed. */
function withoutDates(books: Record<string, Book>): Record<string, Book> {
  return Object.fromEntries(
    Object.entries(books).map(([id, book]) => [id, { ...book, dateRead: null, read: false }]),
  );
}

test('narrows the board to the books a search matches', async ({ page }) => {
  await page.goto(url);

  const search = page.getByRole('searchbox', { name: 'Search' });
  await expect(search).toHaveAttribute('placeholder', 'Title, author or series');

  await search.fill('Bravo');
  await expect(page.getByText('Bravo', { exact: true })).toBeVisible();
  await expect(page.getByText('The </script> Problem', { exact: true })).toHaveCount(0);
  await expect(page.getByText('Zulu', { exact: true })).toHaveCount(0);
  await expect(page.locator('section')).toHaveCount(data.lanes.length);

  await search.fill('');
  await expect(page.getByText('Zulu', { exact: true })).toBeVisible();
});

test('keeps a Stack whose series name answers the search', async ({ page }) => {
  await page.goto(url);

  await page.getByRole('searchbox', { name: 'Search' }).fill('Dune');

  await expect(page.getByRole('figure', { name: 'Dune' })).toBeVisible();
  await expect(page.getByRole('figure', { name: 'Earthsea' })).toHaveCount(0);
  await expect(page.getByText('Another S', { exact: true })).toHaveCount(0);
  await expect(page.locator('section')).toHaveCount(data.lanes.length);
});

test('shows only books meeting an author and a tag together', async ({ page }) => {
  await page.goto(url);

  await page.getByRole('combobox', { name: 'Author' }).selectOption('Ann Author');
  await page.getByRole('combobox', { name: 'Tag' }).selectOption('mystery');

  await expect(page.getByText('The </script> Problem', { exact: true })).toBeVisible();
  await expect(page.getByText('Alpha', { exact: true })).toHaveCount(0);
  await expect(page.getByText('Another S', { exact: true })).toHaveCount(0);
  await expect(page.getByRole('figure')).toHaveCount(0);
});

test('shows only books meeting a tag and a year together', async ({ page }) => {
  await page.goto(url);

  await page.getByRole('combobox', { name: 'Tag' }).selectOption('mystery');
  const year = page.getByRole('combobox', { name: 'Year read' });
  await expect(page.getByText('The </script> Problem', { exact: true })).toBeVisible();

  await year.selectOption('2024');
  await expect(page.getByText('The </script> Problem', { exact: true })).toBeVisible();

  await year.selectOption('2023');
  await expect(page.getByText('The </script> Problem', { exact: true })).toHaveCount(0);
});

test('restores the whole board when a select returns to All', async ({ page }) => {
  await page.goto(url);

  const author = page.getByRole('combobox', { name: 'Author' });
  await author.selectOption('Ann Author');
  await expect(page.getByText('Another S', { exact: true })).toHaveCount(0);

  await author.selectOption('All');
  await expect(page.getByText('Another S', { exact: true })).toBeVisible();
  await expect(page.getByText('Zulu', { exact: true })).toBeVisible();
});

test('hides the year filter and says why when no book has a date', async ({ page }) => {
  await page.goto(await fixtureBoardUrl({ ...data, books: withoutDates(data.books) }));

  await expect(page.getByRole('combobox', { name: 'Year read' })).toHaveCount(0);
  await expect(
    page.getByText('Year filter unavailable: the read column has no dates.'),
  ).toBeVisible();
  await expect(page.getByRole('combobox', { name: 'Author' })).toBeVisible();
  await expect(page.getByRole('searchbox', { name: 'Search' })).toBeVisible();
  await expect(page.getByText('Zulu', { exact: true })).toBeVisible();
});

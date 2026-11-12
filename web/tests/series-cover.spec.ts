import { expect, test, type Page } from '@playwright/test';
import type { TierListData } from '../src/contract/tierlist';
import { fixtureBoardUrl, loadFixture } from './page';

let data: TierListData;
let url: string;

test.beforeAll(async () => {
  data = await loadFixture();
  url = await fixtureBoardUrl();
});

const LABEL = 'Use this cover for the series';

/** Dune with its covered books in order: the first is the default Series Cover, the last an unread pick. */
function dune() {
  const series = data.series['Dune'];
  if (!series) throw new Error('Fixture has no Dune');
  const covered = series.positions.flatMap(({ book }) => (book !== null && book in data.covers ? [book] : []));
  const unread = covered.find((id) => data.books[id]?.read === false);
  if (covered.length < 3 || !unread) throw new Error('Fixture Dune needs three covers, one on an unread book');
  return { series, covered, unread };
}

const src = (id: string) => data.covers[id]?.src ?? '';
const front = (page: Page) => page.getByRole('figure', { name: 'Dune', exact: true }).locator('.cover');

async function openDune(page: Page) {
  await page.goto(url);
  await page.getByRole('figure', { name: 'Dune', exact: true }).getByRole('button').click();
  const panel = page.getByRole('dialog', { name: 'Dune' });
  await expect(panel).toBeVisible();
  const row = (id: string) => panel.getByRole('listitem').filter({ hasText: data.books[id]?.title ?? id });
  return { panel, row, eye: (id: string) => row(id).getByRole('button', { name: LABEL }) };
}

test('offers an eye only on owned books with a cover, keeping every row the same width', async ({ page }) => {
  const { series, covered } = dune();
  const { panel } = await openDune(page);

  const rows = panel.getByRole('listitem');
  for (const [index, position] of series.positions.entries()) {
    const eyes = rows.nth(index).getByRole('button', { name: LABEL });
    await expect(eyes).toHaveCount(position.book !== null && covered.includes(position.book) ? 1 : 0);
    await expect(rows.nth(index).locator('.eye, .eye-slot')).toHaveCount(1);
  }
  const width = async (selector: string) => (await panel.locator(selector).first().boundingBox())?.width ?? 0;
  expect(await width('.eye-slot')).toBeGreaterThan(0);
  expect(await width('.eye-slot')).toBeCloseTo(await width('.eye'), 1);
  await expect(panel.getByRole('button', { name: LABEL }).first()).toHaveAttribute('title', LABEL);
});

test('presses the eye of the default Series Cover and no other', async ({ page }) => {
  const { covered } = dune();
  const { eye } = await openDune(page);

  for (const [index, id] of covered.entries()) {
    await expect(eye(id)).toHaveAttribute('aria-pressed', index === 0 ? 'true' : 'false');
  }
  await expect(front(page)).toHaveAttribute('src', src(covered[0] ?? ''));
});

test('switches the Stack to a picked cover at once and keeps the panel open', async ({ page }) => {
  const { covered, unread } = dune();
  const { panel, eye } = await openDune(page);

  await eye(unread).click();

  await expect(panel).toBeVisible();
  await expect(eye(unread)).toHaveAttribute('aria-pressed', 'true');
  await expect(eye(covered[0] ?? '')).toHaveAttribute('aria-pressed', 'false');
  await expect(front(page)).toHaveAttribute('src', src(unread));
  await expect(front(page)).toHaveCSS('filter', 'none');
  await expect(front(page)).toHaveCSS('opacity', '1');
});

test('returns a picked cover to the default when its eye is pressed again', async ({ page }) => {
  const { covered, unread } = dune();
  const { eye } = await openDune(page);

  await eye(unread).click();
  await eye(unread).click();

  await expect(eye(covered[0] ?? '')).toHaveAttribute('aria-pressed', 'true');
  await expect(front(page)).toHaveAttribute('src', src(covered[0] ?? ''));
});

test('leaves the default cover in place when its pressed eye is clicked', async ({ page }) => {
  const { covered } = dune();
  const { eye } = await openDune(page);

  await eye(covered[0] ?? '').click();

  await expect(eye(covered[0] ?? '')).toHaveAttribute('aria-pressed', 'true');
  await expect(front(page)).toHaveAttribute('src', src(covered[0] ?? ''));
});

test('keeps the pick for the session across closing and reopening the panel, not across a reload', async ({
  page,
}) => {
  const { covered, unread } = dune();
  const { panel, eye } = await openDune(page);
  await eye(unread).click();
  await panel.getByRole('button', { name: 'Close' }).click();

  await expect(front(page)).toHaveAttribute('src', src(unread));
  await page.getByRole('figure', { name: 'Dune', exact: true }).getByRole('button').click();
  await expect(eye(unread)).toHaveAttribute('aria-pressed', 'true');

  await page.reload();
  await expect(front(page)).toHaveAttribute('src', src(covered[0] ?? ''));
});

test('opens Detail from the title, not from the eye', async ({ page }) => {
  const { unread } = dune();
  const { panel, row, eye } = await openDune(page);
  const detail = page.getByRole('dialog', { name: data.books[unread]?.title ?? '' });

  await eye(unread).click();
  await expect(panel).toBeVisible();
  await expect(detail).toBeHidden();

  await row(unread).locator('button.title').click();

  await expect(detail).toBeVisible();
});

test('names each eye after its book for assistive tech', async ({ page }) => {
  const { unread } = dune();
  const { eye } = await openDune(page);

  await expect(eye(unread)).toHaveAccessibleDescription(data.books[unread]?.title ?? '');
});

test('prints the picked Series Cover', async ({ page }) => {
  const { unread } = dune();
  const { panel, eye } = await openDune(page);
  await eye(unread).click();
  await panel.getByRole('button', { name: 'Close' }).click();

  await page.emulateMedia({ media: 'print' });

  await expect(front(page)).toBeVisible();
  await expect(front(page)).toHaveAttribute('src', src(unread));
});

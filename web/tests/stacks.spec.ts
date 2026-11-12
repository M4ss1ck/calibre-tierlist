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
    lane.stacks.filter((name) => name in data.series).map((name) => ({ name, lane: index })),
  );
}

const owned = (name: string) => seriesOf(name).positions.filter((position) => position.book !== null);
const stack = (page: Page, name: string) => page.getByRole('figure', { name, exact: true });

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

test('fills a Stack with no cover with its series colour and dims an unread front', async ({ page }) => {
  await page.goto(url);
  const bare = placed().find(({ name }) => owned(name).every(({ book }) => book === null || !(book in data.covers)));
  if (!bare) throw new Error('Fixture has no Stack without covers');
  const front = owned(bare.name)[0]?.book;
  if (!front || data.books[front]?.read !== false) throw new Error('Fixture bare Stack should front an unread book');

  const button = stack(page, bare.name).locator('.front');
  await expect(button).toHaveCSS('background-image', /linear-gradient/);
  await expect(button).toHaveClass(/\bunread\b/);
});

test('counts owned books over every position, cut ones included', async ({ page }) => {
  await page.goto(url);

  for (const { name } of placed()) {
    const { positions } = seriesOf(name);
    await expect(stack(page, name).locator('.count')).toHaveText(`${owned(name).length}/${positions.length}`);
  }
});

test('names the series in a box and in the button that opens it', async ({ page }) => {
  await page.goto(url);

  for (const { name } of placed()) {
    const total = seriesOf(name).positions.length;
    await expect(stack(page, name).locator('.name')).toHaveText(name);
    await expect(
      stack(page, name).getByRole('button', { name: `${name}, ${owned(name).length} of ${total} books` }),
    ).toBeVisible();
  }
});

test('peeks at most two sheets out behind the front', async ({ page }) => {
  await page.goto(url);

  for (const { name } of placed()) {
    const expected = Math.min(2, seriesOf(name).positions.length - 1);
    await expect(stack(page, name).locator('.behind')).toHaveCount(expected);
  }
});

test('draws no per-position elements, Tier badges or cut badge', async ({ page }) => {
  await page.goto(url);

  for (const selector of ['.position', '.tier-badge', '.more', 'button.toggle']) {
    await expect(page.locator(`figure.stack ${selector}`)).toHaveCount(0);
  }
  for (const { name } of placed()) {
    await expect(stack(page, name).getByRole('button')).toHaveCount(1);
  }
});

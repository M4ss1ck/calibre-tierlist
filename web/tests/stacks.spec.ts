import { expect, test, type Page } from '@playwright/test';
import type { Book, TierListData } from '../src/contract/tierlist';
import { fixtureBoardUrl, loadFixture } from './page';

let data: TierListData;
let url: string;

test.beforeAll(async () => {
  data = await loadFixture();
  url = await fixtureBoardUrl();
});

function seriesOf(name: string) {
  const series = data.series[name];
  if (!series) throw new Error(`Fixture Lane names unknown series ${name}`);
  return series;
}

function bookOf(id: string): Book {
  const book = data.books[id];
  if (!book) throw new Error(`Fixture Stack names unknown book ${id}`);
  return book;
}

function labelOf(id: string): string {
  const tierId = bookOf(id).tier;
  const tier = tierId === null ? undefined : data.tiers.find((candidate) => candidate.id === tierId);
  return tier?.label ?? '-';
}

/** Every Stack the fixture places on the board, with the Lane index that names it. */
function placed(): { name: string; lane: number }[] {
  return data.lanes.flatMap((lane, index) =>
    lane.stacks.filter((name) => name in data.series).map((name) => ({ name, lane: index })),
  );
}

function stack(page: Page, name: string) {
  const lane = data.lanes.findIndex((candidate) => candidate.stacks.includes(name));
  const listed = data.lanes[lane]?.stacks.filter((candidate) => candidate in data.series) ?? [];
  const index = listed.indexOf(name);
  if (lane < 0 || index < 0) throw new Error(`No Lane draws the Stack ${name}`);
  return page.locator('section').nth(lane).locator('figure.stack').nth(index);
}

test('draws each Stack in the Lane that names it, first position in front', async ({ page }) => {
  await page.goto(url);

  for (const { name, lane } of placed()) {
    const figure = stack(page, name);
    await expect(figure).toHaveAttribute('aria-label', name);
    const parent = await figure.evaluate((node) =>
      Array.from(document.querySelectorAll('section')).indexOf(node.closest('section') as HTMLElement),
    );
    expect(parent).toBe(lane);

    const positions = figure.locator('.position');
    const numbers = await positions.evaluateAll((nodes) =>
      nodes.map((node) => node.getAttribute('data-number')),
    );
    expect(numbers).toEqual(seriesOf(name).positions.map((position) => position.number));

    const layers = await positions.evaluateAll((nodes) =>
      nodes.map((node) => Number(getComputedStyle(node).zIndex)),
    );
    expect(layers[0]).toBe(Math.max(...layers));
    expect(layers.slice(1).every((layer) => layer < Number(layers[0]))).toBe(true);
  }
});

test('dims the positions of unread books and leaves read ones alone', async ({ page }) => {
  await page.goto(url);
  let unread = 0;

  for (const { name } of placed()) {
    const positions = stack(page, name).locator('.position');
    for (const [index, position] of seriesOf(name).positions.entries()) {
      if (position.book === null) continue;
      const dimmed = !bookOf(position.book).read;
      const classes = ((await positions.nth(index).getAttribute('class')) ?? '').split(/\s+/);
      expect(classes.includes('unread')).toBe(dimmed);
      unread += dimmed ? 1 : 0;
    }
  }

  expect(unread).toBeGreaterThan(0);
});

test('draws a Placeholder for every position without an owned book', async ({ page }) => {
  await page.goto(url);
  let drawn = 0;

  for (const { name } of placed()) {
    const expected = seriesOf(name).positions.filter((position) => position.book === null);
    const placeholders = stack(page, name).locator('.position.placeholder');
    await expect(placeholders).toHaveCount(expected.length);

    for (const [index, position] of expected.entries()) {
      const placeholder = placeholders.nth(index);
      await expect(placeholder).toHaveAttribute('data-number', position.number);
      await expect(placeholder.locator('.series-name')).toHaveText(name);
      await expect(placeholder.locator('.number')).toHaveText(position.number);
      await expect(placeholder.locator('img')).toHaveCount(0);
      drawn += 1;
    }
  }

  expect(drawn).toBeGreaterThan(0);
});

test('shows how many positions were cut from each Stack', async ({ page }) => {
  await page.goto(url);
  let cut = 0;

  for (const { name } of placed()) {
    const more = seriesOf(name).more;
    const badge = stack(page, name).locator('.more');
    if (more > 0) {
      await expect(badge).toHaveText(`+${more}`);
      cut += 1;
    } else {
      await expect(badge).toHaveCount(0);
    }
  }

  expect(cut).toBeGreaterThan(0);
});

test('labels every owned position with its Book Tier', async ({ page }) => {
  await page.goto(url);
  const seen: string[] = [];

  for (const { name } of placed()) {
    const labels = seriesOf(name).positions.flatMap((position) =>
      position.book === null ? [] : [labelOf(position.book)],
    );
    await expect(stack(page, name).locator('.tier-badge')).toHaveText(labels);
    seen.push(...labels);
  }

  expect(seen).toContain('-');
});

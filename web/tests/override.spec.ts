import { expect, test, type Page } from '@playwright/test';
import type { Series, TierListData } from '../src/contract/tierlist';
import { fixtureBoardUrl, loadFixture } from './page';

let data: TierListData;
let url: string;

test.beforeAll(async () => {
  data = await loadFixture();
  url = await fixtureBoardUrl();
});

/** Every series Stack the fixture places on the board. */
function placed(): string[] {
  return data.lanes.flatMap((lane) => lane.stacks.filter((name) => name in data.series));
}

function seriesOf(name: string): Series {
  const series = data.series[name];
  if (!series) throw new Error(`Fixture Lane names unknown series ${name}`);
  return series;
}

function stack(page: Page, name: string) {
  return page.getByRole('figure', { name });
}

const badgeName = 'Series Tier Override';

test('marks each Override Stack with a visible badge', async ({ page }) => {
  await page.goto(url);

  const overrides = placed().filter((name) => seriesOf(name).override);
  expect(overrides.length).toBeGreaterThan(0);

  for (const name of overrides) {
    const figure = stack(page, name);
    await expect(figure).toHaveAttribute('data-override', 'true');
    const badge = figure.getByRole('img', { name: badgeName });
    await expect(badge).toBeVisible();
    await expect(badge).toHaveAttribute('title', 'Series Tier set by Override');
  }
});

test('leaves each Auto Stack without a badge or data-override', async ({ page }) => {
  await page.goto(url);

  const autos = placed().filter((name) => !seriesOf(name).override);
  expect(autos.length).toBeGreaterThan(0);

  for (const name of autos) {
    const figure = stack(page, name);
    expect(await figure.getAttribute('data-override')).toBeNull();
    await expect(figure.getByRole('img', { name: badgeName })).toHaveCount(0);
  }
});

test('shows one badge per Override Stack on the board', async ({ page }) => {
  await page.goto(url);

  const overrides = placed().filter((name) => seriesOf(name).override);
  await expect(page.getByRole('img', { name: badgeName })).toHaveCount(overrides.length);
});

test('keeps the badge visible in the dark theme', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'dark' });
  await page.goto(url);

  const [name] = placed().filter((candidate) => seriesOf(candidate).override);
  if (!name) throw new Error('Fixture places no Override Stack');
  await expect(stack(page, name).getByRole('img', { name: badgeName })).toBeVisible();
});

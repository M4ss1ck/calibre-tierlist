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
  return data.lanes.flatMap((lane) =>
    lane.items.flatMap((item) => ('stack' in item && item.stack in data.series ? [item.stack] : [])),
  );
}

function seriesOf(name: string): Series {
  const series = data.series[name];
  if (!series) throw new Error(`Fixture Lane names unknown series ${name}`);
  return series;
}

function stack(page: Page, name: string) {
  return page.getByRole('figure', { name });
}

test('marks each Override Stack with data-override', async ({ page }) => {
  await page.goto(url);

  const overrides = placed().filter((name) => seriesOf(name).override);
  expect(overrides.length).toBeGreaterThan(0);

  for (const name of overrides) {
    await expect(stack(page, name)).toHaveAttribute('data-override', 'true');
  }
});

test('leaves each Auto Stack without data-override', async ({ page }) => {
  await page.goto(url);

  const autos = placed().filter((name) => !seriesOf(name).override);
  expect(autos.length).toBeGreaterThan(0);

  for (const name of autos) {
    expect(await stack(page, name).getAttribute('data-override')).toBeNull();
  }
});

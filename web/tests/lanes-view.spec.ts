import { expect, test, type Locator, type Page } from '@playwright/test';
import type { TierListData } from '../src/contract/tierlist';
import { fixtureBoardUrl, loadFixture } from './page';

let data: TierListData;
let url: string;
let emptyUrl: string;

/** The fixture with the A Lane emptied, so the Empty Lane Message has a Lane to show in. */
function withEmptyLane(base: TierListData): TierListData {
  return { ...base, lanes: base.lanes.map((lane) => (lane.tier === 'a' ? { ...lane, items: [] } : lane)) };
}

test.beforeAll(async () => {
  data = await loadFixture();
  url = await fixtureBoardUrl();
  emptyUrl = await fixtureBoardUrl(withEmptyLane(data));
});

/** Open the View Panel, change one control and close it again. */
async function change(page: Page, pick: (panel: Locator) => Promise<void>) {
  await page.getByRole('button', { name: 'Customize view' }).click();
  await pick(page.getByRole('dialog', { name: 'Customize view' }));
  await page.keyboard.press('Escape');
}

const region = (page: Page, name: string) => page.getByRole('region', { name, exact: true });

test('hides every Lane label when Tier labels are off, keeping the regions', async ({ page }) => {
  await page.goto(url);
  await expect(page.locator('section h2')).toHaveCount(data.lanes.length);

  await change(page, (panel) => panel.getByRole('switch', { name: 'Tier labels' }).click());

  await expect(page.locator('section h2')).toHaveCount(0);
  await expect(page.locator('section')).toHaveCount(data.lanes.length);
  for (const name of [...data.tiers.map((tier) => tier.label), 'Unranked']) {
    await expect(region(page, name)).toBeVisible();
  }
});

test('shows a Tier description only when Tier descriptions are on', async ({ page }) => {
  await page.goto(url);
  await expect(page.locator('.description')).toHaveCount(0);

  await change(page, (panel) => panel.getByRole('switch', { name: 'Tier descriptions' }).click());

  await expect(region(page, 'S').locator('.description')).toHaveText('The best');
  await expect(region(page, 'A').locator('.description')).toHaveCount(0);
  await expect(region(page, 'Unranked').locator('.description')).toHaveCount(0);
  await expect(page.locator('.description')).toHaveCount(1);
});

test('shows the default Empty Lane Message in a Lane with nothing drawn in it', async ({ page }) => {
  await page.goto(emptyUrl);
  await expect(region(page, 'A').locator('.empty')).toHaveText('No books in this tier');
});

test('hides the Empty Lane Message from the panel', async ({ page }) => {
  await page.goto(emptyUrl);
  await change(page, (panel) =>
    panel.getByRole('group', { name: 'Empty message' }).getByRole('button', { name: 'Hidden' }).click(),
  );

  await expect(region(page, 'A').locator('.empty')).toHaveCount(0);
});

test('shows the reader their own Empty Lane Message from the address', async ({ page }) => {
  await page.goto(`${emptyUrl}?empty=custom&empty_text=Nothing%20yet`);
  await expect(region(page, 'A').locator('.empty')).toHaveText('Nothing yet');
});

/** The first two Lanes' boxes: the gap between them, and the first one's corner radius. */
async function laneGeometry(page: Page) {
  return page
    .locator('section.lane')
    .evaluateAll((lanes) => {
      const [first, second] = lanes.map((lane) => lane.getBoundingClientRect());
      if (!first || !second) throw new Error('The board needs two Lanes');
      return {
        gap: second.top - first.bottom,
        radius: getComputedStyle(lanes[0] as Element).borderTopLeftRadius,
      };
    });
}

test('draws the Lanes as one block split by lines by default', async ({ page }) => {
  await page.goto(url);
  const { gap, radius } = await laneGeometry(page);

  expect(gap).toBe(0);
  expect(radius).toBe('0px');
});

test('?lane_gap=large spaces the Lanes out as rounded blocks', async ({ page }) => {
  await page.goto(`${url}?lane_gap=large`);
  const { gap, radius } = await laneGeometry(page);

  expect(gap).toBe(28);
  expect(radius).toBe('14px');
});

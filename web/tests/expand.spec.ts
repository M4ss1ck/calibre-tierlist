import { expect, test } from '@playwright/test';
import type { Series, TierListData } from '../src/contract/tierlist';
import { fixtureBoardUrl, loadFixture } from './page';

let data: TierListData;
let url: string;

test.beforeAll(async () => {
  data = await loadFixture();
  url = await fixtureBoardUrl();
});

/** The fixture series whose collapsed Stack cuts positions. */
function cut(): [string, Series] {
  const found = Object.entries(data.series).find(([, series]) => series.more > 0);
  if (!found) throw new Error('Fixture has no Stack with cut positions');
  return found;
}

const numbers = (series: Series) => series.positions.map((position) => position.number);

test('expands a Stack to every position and collapses it again', async ({ page }) => {
  const [name, series] = cut();
  await page.goto(url);

  const stack = page.getByRole('figure', { name });
  const positions = stack.locator('.position');
  const toggle = stack.locator('button.toggle');
  await expect(toggle).toHaveText(`Show all ${series.positions.length}`);
  await expect(positions).toHaveCount(series.positions.length - series.more);
  await expect(toggle).toHaveAttribute('aria-expanded', 'false');

  await toggle.click();
  await expect(toggle).toHaveAttribute('aria-expanded', 'true');
  await expect(toggle).toHaveText('Show fewer');
  await expect(positions).toHaveCount(series.positions.length);
  expect(await positions.evaluateAll((nodes) => nodes.map((node) => node.dataset['number']))).toEqual(
    numbers(series),
  );
  await expect(stack.locator('.more')).toHaveCount(0);

  await toggle.press('Enter');
  await expect(toggle).toHaveAttribute('aria-expanded', 'false');
  await expect(positions).toHaveCount(series.positions.length - series.more);
  await expect(stack.locator('.more')).toHaveText(`+${series.more}`);
});

test('opens the detail panel from a position only the expanded Stack shows', async ({ page }) => {
  const [name, series] = cut();
  const last = series.positions.at(-1);
  if (!last || last.book !== null) throw new Error('Fixture Stack should end in a Placeholder');
  await page.goto(url);

  const stack = page.getByRole('figure', { name });
  const placeholder = stack.getByRole('button', { name: `${name} #${last.number}, not in your library` });
  await expect(placeholder).toHaveCount(0);
  await stack.getByRole('button', { name: /^Show all/ }).click();
  await placeholder.click();
  await expect(page.getByRole('dialog', { name: `${name} #${last.number}` })).toBeVisible();
});

test('offers no expand toggle for a Stack of one position', async ({ page }) => {
  const single = Object.entries(data.series).find(([, series]) => series.positions.length === 1);
  if (!single) throw new Error('Fixture has no single-position Stack');
  await page.goto(url);

  await expect(page.getByRole('figure', { name: single[0] }).locator('.toggle')).toHaveCount(0);
});

test('toggles the Unranked Lane off and on', async ({ page }) => {
  await page.goto(url);

  const toggle = page.getByRole('button', { name: 'Unranked Lane' });
  const lane = page.getByRole('region', { name: 'Unranked' });
  await expect(toggle).toHaveAttribute('aria-pressed', 'true');
  await expect(lane).toBeVisible();

  await toggle.click();
  await expect(toggle).toHaveAttribute('aria-pressed', 'false');
  await expect(lane).toHaveCount(0);
  await expect(page.locator('section')).toHaveCount(data.tiers.length);

  await toggle.click();
  await expect(toggle).toHaveAttribute('aria-pressed', 'true');
  await expect(lane).toBeVisible();
});

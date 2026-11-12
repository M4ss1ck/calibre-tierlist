import { expect, test, type Page } from '@playwright/test';
import type { TierListData } from '../src/contract/tierlist';
import { fixtureBoardUrl, loadFixture } from './page';

let data: TierListData;
let url: string;

test.beforeAll(async () => {
  data = await loadFixture();
  url = await fixtureBoardUrl();
});

/** Open the View Panel, where the Unranked Lane switch now lives. */
async function openPanel(page: Page) {
  await page.getByRole('button', { name: 'Customize view' }).click();
  const dialog = page.getByRole('dialog', { name: 'Customize view' });
  await expect(dialog).toBeVisible();
  return dialog;
}

test('switches the Unranked Lane off and on from the View Panel', async ({ page }) => {
  await page.goto(url);
  const panel = await openPanel(page);

  const toggle = panel.getByRole('switch', { name: 'Unranked lane' });
  const lane = page.getByRole('region', { name: 'Unranked' });
  await expect(toggle).toHaveAttribute('aria-checked', 'true');
  await expect(lane).toBeVisible();

  await toggle.click();
  await expect(toggle).toHaveAttribute('aria-checked', 'false');
  await expect(lane).toHaveCount(0);
  await expect(page.locator('section')).toHaveCount(data.tiers.length);

  await toggle.press('Space');
  await expect(toggle).toHaveAttribute('aria-checked', 'true');
  await expect(lane).toBeVisible();
});

test('toggles from its visible label too', async ({ page }) => {
  await page.goto(url);
  const panel = await openPanel(page);

  await panel.getByText('Unranked lane', { exact: true }).click();
  await expect(panel.getByRole('switch', { name: 'Unranked lane' })).toHaveAttribute('aria-checked', 'false');
  await expect(page.getByRole('region', { name: 'Unranked' })).toHaveCount(0);
});

import { expect, test } from '@playwright/test';
import { fixtureBoardUrl } from './page';
import { printMedia } from './print';

test('prints the light palette even with the dark theme on', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'light' });
  await page.goto(await fixtureBoardUrl());
  await expect(page.locator('.card').first()).toBeAttached();

  // The page and a Lane's card well: every surface the dark palette repaints.
  const background = () =>
    page.evaluate(() =>
      ['body', '.lane .cards'].map((selector) => {
        const element = document.querySelector(selector);
        if (!element) throw new Error(`No ${selector} on the board`);
        return getComputedStyle(element).backgroundColor;
      }),
    );
  const light = await background();

  const dark = page.getByRole('group', { name: 'Theme' }).getByRole('button', { name: 'Dark' });
  await dark.click();
  await expect(dark).toHaveAttribute('aria-pressed', 'true');
  const shown = await background();
  expect(shown[0]).not.toBe(light[0]);
  expect(shown[1]).not.toBe(light[1]);

  // The picker is off the paper, but the palette it chose is overruled there.
  await page.emulateMedia({ media: 'print' });
  expect(await background()).toEqual(light);
});

test('drops the controls and the Detail Panel from the paper', async ({ page }) => {
  await printMedia(page);
  await expect(page.locator('.card').first()).toBeAttached();
  await page.locator('.card button').first().click();
  await expect(page.locator('dialog.detail')).toHaveAttribute('open', '');

  for (const control of [
    page.locator('form.filters'),
    page.locator('input[type="search"]'),
    page.getByRole('switch', { name: 'Unranked lane', includeHidden: true }),
    page.getByRole('group', { name: 'Theme', includeHidden: true }),
    page.getByRole('button', { name: 'Download PNG', includeHidden: true }),
    page.getByRole('button', { name: 'Print or PDF', includeHidden: true }),
    page.getByRole('status', { includeHidden: true }),
    page.locator('dialog.detail'),
  ]) {
    await expect(control).toBeHidden();
  }

  // The board itself is what the paper is for, so it stays, title and all.
  await expect(page.getByRole('heading', { level: 1, name: 'Tier List' })).toBeVisible();
  await expect(page.locator('.lanes')).toBeVisible();
  await expect(page.locator('.card').first()).toBeVisible();
  await expect(page.getByRole('region', { name: 'S', exact: true })).toBeVisible();
});

test('drops an open series panel from the paper but keeps its Stack', async ({ page }) => {
  await printMedia(page);
  await page.getByRole('figure', { name: 'Dune' }).getByRole('button').click();
  const panel = page.locator('dialog.series-panel');
  await expect(panel).toHaveAttribute('open', '');

  await expect(panel).toBeHidden();
  await expect(page.getByRole('figure', { name: 'Dune' })).toBeVisible();
});

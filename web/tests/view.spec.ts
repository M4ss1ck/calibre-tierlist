import { expect, test, type Page } from '@playwright/test';
import { oversized } from './fixture';
import { fixtureBoardUrl } from './page';

let url: string;

test.beforeAll(async () => {
  url = await fixtureBoardUrl();
});

const trigger = (page: Page) => page.getByRole('button', { name: 'Customize view' });
const panel = (page: Page) => page.getByRole('dialog', { name: 'Customize view' });
const maxWidth = (page: Page) => page.locator('main.board').evaluate((board) => getComputedStyle(board).maxWidth);

/** Open the View Panel and hand it back. */
async function openPanel(page: Page) {
  await trigger(page).click();
  const dialog = panel(page);
  await expect(dialog).toBeVisible();
  return dialog;
}

test('opens from Customize view and closes on Escape, returning focus to it', async ({ page }) => {
  await page.goto(url);
  await expect(panel(page)).toHaveCount(0);

  await openPanel(page);
  await expect(trigger(page)).toHaveAttribute('aria-expanded', 'true');

  await page.keyboard.press('Escape');
  await expect(panel(page)).toHaveCount(0);
  await expect(trigger(page)).toBeFocused();
  await expect(trigger(page)).toHaveAttribute('aria-expanded', 'false');
});

test('closes on a click outside it', async ({ page }) => {
  await page.goto(url);
  await openPanel(page);

  await page.mouse.click(10, 10);
  await expect(panel(page)).toHaveCount(0);
});

test('resets every control to the page defaults', async ({ page }) => {
  await page.goto(url);
  await openPanel(page);

  const captions = page.getByRole('switch', { name: 'Captions' });
  await captions.click();
  await expect(captions).toHaveAttribute('aria-checked', 'false');
  await expect(page.locator('.name, .title')).toHaveCount(0);

  await page.getByRole('button', { name: 'Reset to page defaults' }).click();
  await expect(captions).toHaveAttribute('aria-checked', 'true');
  await expect(page.locator('.name').first()).toBeVisible();
});

test('draws the board at the normal Page Width by default', async ({ page }) => {
  await page.goto(url);
  expect(await maxWidth(page)).toBe('1360px');
});

test('?width=full lets the board use the whole window', async ({ page }) => {
  await page.goto(`${url}?width=full`);
  expect(await maxWidth(page)).toBe('none');
});

test('the panel narrows the board', async ({ page }) => {
  await page.goto(url);
  await openPanel(page);

  const width = page.getByRole('group', { name: 'Page width' });
  await width.getByRole('button', { name: 'Narrow' }).click();
  await page.keyboard.press('Escape');
  expect(await maxWidth(page)).toBe('960px');
});

test('wraps a crowded Lane onto more than one row', async ({ page }) => {
  await page.goto(await fixtureBoardUrl(await oversized()));

  const rows = await page
    .locator('section')
    .first()
    .locator('.card')
    .evaluateAll((cards) => new Set(cards.map((card) => (card as HTMLElement).offsetTop)).size);

  expect(rows).toBeGreaterThan(1);
});

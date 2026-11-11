import { expect, test, type Page } from '@playwright/test';
import { fixtureBoardUrl } from './page';

let url: string;

test.beforeAll(async () => {
  url = await fixtureBoardUrl();
});

const darkToggle = (page: Page) => page.getByRole('button', { name: 'Dark theme' });

/** The painted page background, which is what the theme actually changes. */
const background = (page: Page) =>
  page.evaluate(() => getComputedStyle(document.body).backgroundColor);

/** The theme the toggle pinned on the root, or null while the system decides. */
const pinned = (page: Page) =>
  page.evaluate(() => document.documentElement.dataset['theme'] ?? null);

test('follows the system dark preference without pinning a theme', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'light' });
  await page.goto(url);
  const light = await background(page);
  await expect(darkToggle(page)).toHaveAttribute('aria-pressed', 'false');
  expect(await pinned(page)).toBeNull();

  await page.emulateMedia({ colorScheme: 'dark' });
  await page.reload();
  await expect(darkToggle(page)).toHaveAttribute('aria-pressed', 'true');
  expect(await background(page)).not.toBe(light);
  expect(await pinned(page)).toBeNull();
});

test('flips aria-pressed, data-theme and the background on each click', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'light' });
  await page.goto(url);
  const light = await background(page);
  const toggle = darkToggle(page);
  const root = page.locator('html');

  await expect(toggle).toHaveAttribute('aria-pressed', 'false');

  await toggle.click();
  await expect(toggle).toHaveAttribute('aria-pressed', 'true');
  expect(await pinned(page)).toBe('dark');
  await expect(root).toHaveCSS('color-scheme', 'dark');
  const dark = await background(page);
  expect(dark).not.toBe(light);

  await toggle.click();
  await expect(toggle).toHaveAttribute('aria-pressed', 'false');
  expect(await pinned(page)).toBe('light');
  await expect(root).toHaveCSS('color-scheme', 'light');
  expect(await background(page)).toBe(light);
});

test('pins light over a dark system', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'dark' });
  await page.goto(url);
  const dark = await background(page);
  const toggle = darkToggle(page);

  await toggle.click();
  await expect(toggle).toHaveAttribute('aria-pressed', 'false');
  expect(await pinned(page)).toBe('light');
  await expect(page.locator('html')).toHaveCSS('color-scheme', 'light');
  expect(await background(page)).not.toBe(dark);
});

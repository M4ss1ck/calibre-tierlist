import { expect, test, type Page } from '@playwright/test';
import { fixtureBoardUrl } from './page';

let url: string;

test.beforeAll(async () => {
  url = await fixtureBoardUrl();
});

const choice = (page: Page, name: 'System' | 'Light' | 'Dark') =>
  page.getByRole('group', { name: 'Theme' }).getByRole('button', { name, exact: true });

/** The one choice the picker shows as pressed. */
async function expectPressed(page: Page, name: 'System' | 'Light' | 'Dark') {
  for (const option of ['System', 'Light', 'Dark'] as const) {
    await expect(choice(page, option)).toHaveAttribute('aria-pressed', String(option === name));
  }
}

/** The painted page background, which is what the theme actually changes. */
const background = (page: Page) => page.evaluate(() => getComputedStyle(document.body).backgroundColor);

/** The theme pinned on the root, or null while the system decides. */
const pinned = (page: Page) => page.evaluate(() => document.documentElement.dataset['theme'] ?? null);

test('starts on System, pins nothing and follows a live system change', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'light' });
  await page.goto(url);
  const light = await background(page);
  await expectPressed(page, 'System');
  expect(await pinned(page)).toBeNull();

  await page.emulateMedia({ colorScheme: 'dark' });
  await expect.poll(() => background(page)).not.toBe(light);
  await expect(page.locator('html')).toHaveCSS('color-scheme', 'dark');
  await expectPressed(page, 'System');
  expect(await pinned(page)).toBeNull();
});

test('pins Dark over a light system and unpins it with System', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'light' });
  await page.goto(url);
  const light = await background(page);
  const root = page.locator('html');

  await choice(page, 'Dark').click();
  await expectPressed(page, 'Dark');
  expect(await pinned(page)).toBe('dark');
  await expect(root).toHaveCSS('color-scheme', 'dark');
  expect(await background(page)).not.toBe(light);

  await choice(page, 'System').click();
  await expectPressed(page, 'System');
  expect(await pinned(page)).toBeNull();
  await expect(root).toHaveCSS('color-scheme', 'light');
  expect(await background(page)).toBe(light);
});

test('pins Light over a dark system and holds it through a system change', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'dark' });
  await page.goto(url);
  const dark = await background(page);

  await choice(page, 'Light').click();
  await expectPressed(page, 'Light');
  expect(await pinned(page)).toBe('light');
  await expect(page.locator('html')).toHaveCSS('color-scheme', 'light');
  const light = await background(page);
  expect(light).not.toBe(dark);

  await page.emulateMedia({ colorScheme: 'light' });
  await page.emulateMedia({ colorScheme: 'dark' });
  expect(await background(page)).toBe(light);
  expect(await pinned(page)).toBe('light');
});

test('pins the same palette the system shows when chosen explicitly', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'dark' });
  await page.goto(url);

  await choice(page, 'Dark').click();
  expect(await pinned(page)).toBe('dark');
  await page.emulateMedia({ colorScheme: 'light' });
  await expect(page.locator('html')).toHaveCSS('color-scheme', 'dark');
});

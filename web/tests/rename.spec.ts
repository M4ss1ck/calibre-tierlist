import { expect, test, type Locator, type Page } from '@playwright/test';
import { fixtureBoardUrl } from './page';

let url: string;

test.beforeAll(async () => {
  url = await fixtureBoardUrl();
});

const title = (page: Page) => page.getByRole('heading', { level: 1 });
const label = (page: Page, name: string) =>
  page.getByRole('region', { name, exact: true }).getByRole('heading', { level: 2 });

/** Focus an editable heading, replace its whole text with `text` and finish with `key`. */
async function retype(heading: Locator, text: string, key: 'Enter' | 'Escape') {
  await heading.click();
  await heading.press('ControlOrMeta+a');
  if (text === '') await heading.press('Delete');
  else await heading.pressSequentially(text);
  await heading.press(key);
}

test('renames the title on Enter and follows it in the document title', async ({ page }) => {
  await page.goto(url);
  await expect(title(page)).toHaveText('Tier List');

  await retype(title(page), 'My Shelf', 'Enter');
  await expect(title(page)).toHaveText('My Shelf');
  await expect(title(page)).not.toBeFocused();
  await expect(page).toHaveTitle('My Shelf');
});

test('reverts the title on Escape and on an empty edit', async ({ page }) => {
  await page.goto(url);

  await retype(title(page), 'Thrown away', 'Escape');
  await expect(title(page)).toHaveText('Tier List');
  await expect(page).toHaveTitle('Tier List');

  await retype(title(page), '', 'Enter');
  await expect(title(page)).toHaveText('Tier List');
  await retype(title(page), '   ', 'Enter');
  await expect(title(page)).toHaveText('Tier List');
});

test('collapses runs of whitespace and commits when focus leaves', async ({ page }) => {
  await page.goto(url);

  await title(page).click();
  await title(page).press('ControlOrMeta+a');
  await title(page).pressSequentially('  Read   next  ');
  await page.locator('footer').click();
  await expect(title(page)).toHaveText('Read next');
  await expect(page).toHaveTitle('Read next');
});

test('renames a tier label on Enter and the Lane region follows it', async ({ page }) => {
  await page.goto(url);

  await retype(label(page, 'S'), 'Must read', 'Enter');
  const renamed = label(page, 'Must read');
  await expect(renamed).toHaveText('Must read');
  await expect(page.getByRole('region', { name: 'S', exact: true })).toHaveCount(0);
  await expect(page.getByRole('region', { name: 'Must read' })).toHaveAttribute('data-lane-id', 's');
  await expect(renamed).toHaveClass(/\blong\b/);
});

test('reverts a tier label on Escape and on an empty edit', async ({ page }) => {
  await page.goto(url);

  await retype(label(page, 'A'), 'Nope', 'Escape');
  await expect(label(page, 'A')).toHaveText('A');

  await retype(label(page, 'A'), '', 'Enter');
  await expect(label(page, 'A')).toHaveText('A');
  await expect(page.getByRole('region', { name: 'A', exact: true })).toHaveCount(1);
});

test('keeps a renamed Unranked label when the Lane is switched off and on', async ({ page }) => {
  await page.goto(url);

  await retype(label(page, 'Unranked'), 'Someday', 'Enter');
  await page.getByRole('button', { name: 'Customize view' }).click();
  const toggle = page.getByRole('switch', { name: 'Unranked lane' });
  await expect(toggle).toBeVisible();
  await toggle.click();
  await expect(page.getByRole('region', { name: 'Someday' })).toHaveCount(0);
  await toggle.click();
  await page.keyboard.press('Escape');
  await expect(label(page, 'Someday')).toHaveText('Someday');
});

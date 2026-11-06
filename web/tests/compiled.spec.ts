import { pathToFileURL } from 'node:url';
import { expect, test } from '@playwright/test';

const compiled = process.env['COMPILED_HTML'] ?? '';

test.skip(compiled === '', 'set COMPILED_HTML to the compiled board');

test('shows the compiled lanes and escaped titles without errors', async ({ page }) => {
  const errors: string[] = [];
  const requests: string[] = [];
  page.on('pageerror', (error) => errors.push(error.message));
  page.on('request', (request) => requests.push(request.url()));

  const url = pathToFileURL(compiled).href;
  await page.goto(url);

  const lanes = page.locator('section');
  await expect(lanes.first()).toBeVisible();
  await expect(lanes.last()).toBeVisible();
  await expect(lanes.first()).toHaveAttribute('aria-label', 'S');
  await expect(lanes.last()).toHaveAttribute('aria-label', 'Unranked');

  await expect(page.getByText('The </script> Problem', { exact: true })).toBeVisible();
  await expect(page.getByText('Alpha', { exact: true })).toBeVisible();
  await expect(page.getByText('Unread', { exact: true })).toHaveCount(0);

  expect(errors).toEqual([]);
  expect(requests).toEqual([url]);
});

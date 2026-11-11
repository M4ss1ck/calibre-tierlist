import { readFile } from 'node:fs/promises';
import { expect, test, type Download, type Page } from '@playwright/test';
import { unzipSync } from 'fflate';
import { SAFE_LIMITS } from '../src/export/plan';
import { oversized } from './fixture';
import { fixtureBoardUrl } from './page';

const PNG_SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

function startsWithPng(bytes: Uint8Array): boolean {
  return PNG_SIGNATURE.every((byte, index) => bytes[index] === byte);
}

async function saved(download: Download): Promise<Uint8Array> {
  const path = await download.path();
  if (!path) throw new Error(`Download ${download.suggestedFilename()} has no path`);
  return new Uint8Array(await readFile(path));
}

const exportButton = (page: Page) => page.getByRole('button', { name: 'Export PNG' });

test('downloads the board as tierlist.png and reports it', async ({ page }) => {
  await page.goto(await fixtureBoardUrl());

  const pending = page.waitForEvent('download');
  await exportButton(page).click();
  const download = await pending;

  expect(download.suggestedFilename()).toBe('tierlist.png');
  expect(startsWithPng(await saved(download))).toBe(true);
  await expect(page.getByRole('status')).toHaveText('Exported tierlist.png');
});

test.describe('an oversized board', () => {
  test.use({ deviceScaleFactor: 2 });

  test('downloads one PNG per Lane in order inside tierlist.zip', async ({ page }) => {
    await page.goto(await fixtureBoardUrl(await oversized()));

    const board = await page
      .locator('.lanes')
      .evaluate((element) => ({ width: element.scrollWidth, height: element.scrollHeight }));
    expect((board.width * 2) * (board.height * 2)).toBeGreaterThan(SAFE_LIMITS.maxArea);

    const pending = page.waitForEvent('download');
    await exportButton(page).click();
    const download = await pending;

    expect(download.suggestedFilename()).toBe('tierlist.zip');
    const entries = unzipSync(await saved(download));
    const names = Object.keys(entries).sort();
    expect(names).toEqual(['01-s.png', '02-a.png', '03-b.png', '04-unranked.png']);
    for (const name of names) {
      expect(startsWithPng(entries[name] ?? new Uint8Array())).toBe(true);
    }
    await expect(page.getByRole('status')).toHaveText('Exported 4 lanes as tierlist.zip');
  });
});

test('makes no network request while exporting', async ({ page }) => {
  const url = await fixtureBoardUrl();
  const control = 'https://example.invalid/x';
  const requests: string[] = [];
  page.on('request', (request) => requests.push(request.url()));

  await page.goto(url);
  await expect(page.locator('article').first()).toBeVisible();

  const pending = page.waitForEvent('download');
  await exportButton(page).click();
  await pending;

  await page.evaluate((target) => fetch(target).catch(() => {}), control);
  expect(requests).toContain(control);

  const extra = requests.filter(
    (request) =>
      request !== url &&
      request !== control &&
      !request.startsWith('data:') &&
      !request.startsWith('blob:'),
  );
  expect(extra).toEqual([]);
});

import { readFile } from 'node:fs/promises';
import { expect, test, type Download, type Page } from '@playwright/test';
import { unzipSync } from 'fflate';
import type { Book, Lane, Tier, TierListData } from '../src/contract/tierlist';
import { SAFE_LIMITS } from '../src/export/plan';
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

/** A board with many cards per Lane, tall enough to exceed SAFE_LIMITS at scale 2. */
function oversized(): TierListData {
  const tiers: Tier[] = [
    { id: 's', label: 'S', colour: '#ff7f7f', description: '' },
    { id: 'a', label: 'A', colour: '#ffbf7f', description: '' },
    { id: 'b', label: 'B', colour: '#ffdf7f', description: '' },
  ];
  const books: Record<string, Book> = {};
  const lanes: Lane[] = tiers.map((tier) => {
    const cards: string[] = [];
    for (let index = 0; index < 40; index += 1) {
      const id = `${tier.id}-${index}`;
      books[id] = {
        title: `${tier.label} book ${index + 1}`,
        authors: [],
        series: null,
        seriesIndex: null,
        rating: null,
        tags: [],
        blurb: null,
        tier: tier.id,
        dateRead: null,
        read: true,
      };
      cards.push(id);
    }
    return { tier: tier.id, cards, stacks: [] };
  });

  return {
    schemaVersion: 6,
    generated: {
      at: '2026-11-11T12:00:00+00:00',
      libraryName: 'Oversized Library',
      scope: 'library',
      pluginVersion: '0.1.0',
    },
    tiers,
    lanes,
    books,
    series: {},
    covers: {},
  };
}

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
    await page.goto(await fixtureBoardUrl(oversized()));

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
    expect(names).toEqual(['01-s.png', '02-a.png', '03-b.png']);
    for (const name of names) {
      expect(startsWithPng(entries[name] ?? new Uint8Array())).toBe(true);
    }
    await expect(page.getByRole('status')).toHaveText('Exported 3 tiers as tierlist.zip');
  });
});

test('makes no network request while exporting', async ({ page }) => {
  const url = await fixtureBoardUrl();
  const requests: string[] = [];
  page.on('request', (request) => requests.push(request.url()));

  await page.goto(url);
  await expect(page.locator('article').first()).toBeVisible();

  const pending = page.waitForEvent('download');
  await exportButton(page).click();
  await pending;

  const extra = requests.filter(
    (request) => request !== url && !request.startsWith('data:') && !request.startsWith('blob:'),
  );
  expect(extra).toEqual([]);
});

import { expect, test, type Page } from '@playwright/test';
import type { TierListData } from '../src/contract/tierlist';
import { oversized } from './fixture';
import { fixtureBoardUrl } from './page';

/** A4 at the 96dpi CSS reference, less the 12mm margins `print.css` asks for. */
const MM = 96 / 25.4;
const PAGE = { width: 186 * MM, height: 273 * MM };
const MARGIN = { top: '12mm', bottom: '12mm', left: '12mm', right: '12mm' };

/** Lay the board out the way the PDF is drawn: A4 paper, print media. */
async function printMedia(page: Page, data?: TierListData) {
  await page.setViewportSize({ width: Math.round(PAGE.width), height: Math.round(PAGE.height) });
  await page.emulateMedia({ media: 'print' });
  await page.goto(await fixtureBoardUrl(data));
}

/** `/Type /Page` objects in the PDF, without the `/Type /Pages` tree node. */
function countPages(pdf: Buffer): number {
  return [...pdf.toString('latin1').matchAll(/\/Type\s*\/Page\b(?!s)/g)].length;
}

/** The pages the laid-out board needs, and the PDF it prints to. */
async function printed(page: Page) {
  // The board's own end, not the document's: `min-height: 100vh` pads the rest.
  const height = await page.evaluate(() => {
    const board = document.querySelector('main.board');
    if (!board) throw new Error('The board is missing');
    const box = board.getBoundingClientRect();
    return box.bottom + window.scrollY;
  });
  const pdf = await page.pdf({ format: 'A4', margin: MARGIN, printBackground: true });
  return { needed: Math.ceil(height / PAGE.height), pdf, pages: countPages(pdf) };
}

test('prints the fixture board as a valid A4 PDF', async ({ page }) => {
  await printMedia(page);
  await expect(page.locator('.card').first()).toBeAttached();

  const { needed, pdf, pages } = await printed(page);

  expect(pdf.subarray(0, 5).toString()).toBe('%PDF-');
  expect(pages).toBeGreaterThanOrEqual(1);
  expect(pages).toBe(needed);
});

test('spills an oversized board over more than one page', async ({ page }) => {
  await printMedia(page, await oversized());
  await expect(page.locator('.card').first()).toBeAttached();

  const { needed, pdf, pages } = await printed(page);

  expect(pdf.subarray(0, 5).toString()).toBe('%PDF-');
  expect(pages).toBeGreaterThan(1);
  // A break that keeps a Card whole can only add pages, never remove one.
  expect(pages).toBeGreaterThanOrEqual(needed);
});

test('keeps every Stack and Card whole across a page break', async ({ page }) => {
  await printMedia(page);
  await expect(page.locator('.card').first()).toBeAttached();

  // Print media lays the document out continuously, so where a page break
  // falls is only decided while printing: ask the stylesheet instead.
  const breaks = await page.evaluate(() => {
    const values = (selector: string) =>
      [...document.querySelectorAll(selector)].map((element) => getComputedStyle(element).breakInside);
    const label = document.querySelector('.lane > .label');
    return {
      stacks: values('.stack'),
      cards: values('.card'),
      label: label ? getComputedStyle(label).breakAfter : null,
    };
  });

  expect(breaks.stacks.length).toBeGreaterThan(0);
  expect(breaks.cards.length).toBeGreaterThan(0);
  expect(breaks.stacks.filter((value) => value !== 'avoid')).toEqual([]);
  expect(breaks.cards.filter((value) => value !== 'avoid')).toEqual([]);
  expect(breaks.label).toBe('avoid');
});

test('saves the board as a PDF by calling window.print once', async ({ page }) => {
  // The print dialog would block, so record the call instead of opening it.
  await page.addInitScript(() => {
    const probe = window as Window & { prints?: number };
    probe.prints = 0;
    window.print = () => {
      probe.prints = (probe.prints ?? 0) + 1;
    };
  });
  await page.goto(await fixtureBoardUrl());
  await expect(page.locator('.card').first()).toBeAttached();

  await page.getByRole('button', { name: 'Save as PDF' }).click();

  const prints = await page.evaluate(() => (window as Window & { prints?: number }).prints);
  expect(prints).toBe(1);
});

test('drops the controls and the Detail Panel from the paper', async ({ page }) => {
  await printMedia(page);
  await expect(page.locator('.card').first()).toBeAttached();
  await page.locator('.card button').first().click();
  await expect(page.getByRole('dialog', { includeHidden: true })).toBeAttached();

  for (const control of [
    page.locator('form.filters'),
    page.locator('input[type="search"]'),
    page.getByRole('button', { name: 'Unranked Lane', includeHidden: true }),
    page.getByRole('button', { name: 'Dark theme', includeHidden: true }),
    page.getByRole('button', { name: 'Export PNG', includeHidden: true }),
    page.getByRole('button', { name: 'Save as PDF', includeHidden: true }),
    page.getByRole('status', { includeHidden: true }),
    page.getByRole('dialog', { includeHidden: true }),
  ]) {
    await expect(control).toBeHidden();
  }

  // The board itself is what the paper is for, so it stays.
  await expect(page.locator('.card').first()).toBeVisible();
  await expect(page.getByRole('region', { name: 'S', exact: true })).toBeVisible();
});

import { expect, test, type Page } from '@playwright/test';
import { oversized } from './fixture';
import { fixtureBoardUrl } from './page';
import { PAGE, printMedia } from './print';

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
  const pdf = await page.pdf({ format: 'A4', preferCSSPageSize: true, printBackground: true });
  return { needed: Math.ceil(height / PAGE.height), pdf, pages: countPages(pdf) };
}

test('prints the fixture board as a valid A4 PDF', async ({ page }) => {
  await printMedia(page);
  await expect(page.locator('.card').first()).toBeAttached();

  const { needed, pdf, pages } = await printed(page);

  expect(pdf.subarray(0, 5).toString()).toBe('%PDF-');
  expect(pages).toBeGreaterThanOrEqual(1);
  // A break that keeps a Card whole can only add pages, never remove one.
  expect(pages).toBeGreaterThanOrEqual(needed);
  expect(pages).toBeLessThanOrEqual(needed + 1);
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
    return {
      stacks: values('.stack'),
      cards: values('.card'),
    };
  });

  expect(breaks.stacks.length).toBeGreaterThan(0);
  expect(breaks.cards.length).toBeGreaterThan(0);
  expect(breaks.stacks.filter((value) => value !== 'avoid')).toEqual([]);
  expect(breaks.cards.filter((value) => value !== 'avoid')).toEqual([]);
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

  await page.getByRole('button', { name: 'Print or PDF' }).click();

  const prints = await page.evaluate(() => (window as Window & { prints?: number }).prints);
  expect(prints).toBe(1);
});

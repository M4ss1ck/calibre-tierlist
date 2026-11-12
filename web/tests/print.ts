import type { Page } from '@playwright/test';
import type { TierListData } from '../src/contract/tierlist';
import { fixtureBoardUrl } from './page';

/**
 * A4 at the 96dpi CSS reference, less the 12mm margins `print.css` asks for:
 * `PAGE` mirrors the `@page` rule, since the PDF takes its paper from there.
 */
const MM = 96 / 25.4;
export const PAGE = { width: 186 * MM, height: 273 * MM };

/** Lay the board out the way the PDF is drawn: A4 paper, print media. */
export async function printMedia(page: Page, data?: TierListData) {
  await page.setViewportSize({ width: Math.round(PAGE.width), height: Math.round(PAGE.height) });
  await page.emulateMedia({ media: 'print' });
  await page.goto(await fixtureBoardUrl(data));
}

import { mkdtemp, readFile, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import type { TierListData } from '../src/contract/tierlist';

const templateFile = new URL('../dist/template.html', import.meta.url);
const fixtureFile = new URL('../../contract/fixtures/tierlist.json', import.meta.url);

/** The contract fixture every board test renders. */
export async function loadFixture(): Promise<TierListData> {
  return JSON.parse(await readFile(fixtureFile, 'utf8')) as TierListData;
}

/**
 * Fill the built template with the fixture the way the plugin does and return
 * a file:// URL for the resulting self-contained page.
 */
export async function fixtureBoardUrl(): Promise<string> {
  const template = await readFile(templateFile, 'utf8');
  const payload = JSON.stringify(await loadFixture()).replaceAll('</', '<\\/');
  const html = template.replace('__TIERLIST_DATA__', () => payload);

  const directory = await mkdtemp(join(tmpdir(), 'tierlist-board-'));
  const file = join(directory, 'board.html');
  await writeFile(file, html, 'utf8');

  return pathToFileURL(file).href;
}

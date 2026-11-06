import type { TierListData } from './tierlist';

const DATA_ELEMENT_ID = 'tierlist-data';

/** Read the Tier List Data the plugin embedded in this page. */
export function loadTierListData(doc: Document = document): TierListData {
  const element = doc.getElementById(DATA_ELEMENT_ID);

  if (!element) {
    throw new Error(
      `Missing <script id="${DATA_ELEMENT_ID}"> in template.html: the board was not compiled with Tier List Data.`,
    );
  }

  return JSON.parse(element.textContent ?? '') as TierListData;
}

import type { PageDefaults } from '../contract/tierlist';

/** The values a compiled page falls back to when neither its payload nor the query supplies a choice. */
const BUILT_IN: PageDefaults = {
  theme: 'system',
  title: 'Tier List',
  unrankedLabel: 'Unranked',
  showUnranked: true,
  showCounts: true,
  showLibrary: true,
};

/** The query's values, keeping the last one when a key repeats. */
function queryValues(search: string): Map<string, string> {
  const values = new Map<string, string>();
  for (const [key, value] of new URLSearchParams(search)) values.set(key, value);
  return values;
}

function chosenTheme(value: string | undefined, fallback: PageDefaults['theme']): PageDefaults['theme'] {
  return value === 'system' || value === 'light' || value === 'dark' ? value : fallback;
}

function chosenSwitch(value: string | undefined, fallback: boolean): boolean {
  if (value === '1' || value === 'true') return true;
  if (value === '0' || value === 'false') return false;
  return fallback;
}

function chosenText(value: string | undefined, fallback: string): string {
  return value !== undefined && value.trim() !== '' ? value : fallback;
}

/**
 * The Page Defaults one opening uses: a query key wins over the baked value, which wins over the
 * built-in default. Unknown keys and invalid values are ignored for that key only.
 */
export function resolvePageDefaults(baked: Partial<PageDefaults>, search: string): PageDefaults {
  const query = queryValues(search);
  const defaults: PageDefaults = { ...BUILT_IN, ...baked };

  return {
    theme: chosenTheme(query.get('theme'), defaults.theme),
    title: chosenText(query.get('title'), defaults.title),
    unrankedLabel: chosenText(query.get('unranked_label'), defaults.unrankedLabel),
    showUnranked: chosenSwitch(query.get('unranked'), defaults.showUnranked),
    showCounts: chosenSwitch(query.get('counts'), defaults.showCounts),
    showLibrary: chosenSwitch(query.get('library'), defaults.showLibrary),
  };
}

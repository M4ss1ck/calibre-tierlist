/** The board's two palettes. */
export type Theme = 'light' | 'dark';

/** What the theme picker offers: follow the system, or pin one palette. Not persisted. */
export type ThemeChoice = 'system' | Theme;

/**
 * Show `choice`: `data-theme` on the root pins the light or dark tokens, and its
 * `color-scheme` rule makes the browser's own controls follow. `'system'`
 * removes the attribute, so the board follows the system again.
 */
export function applyTheme(choice: ThemeChoice): void {
  const root = document.documentElement;
  if (choice === 'system') delete root.dataset['theme'];
  else root.dataset['theme'] = choice;
}

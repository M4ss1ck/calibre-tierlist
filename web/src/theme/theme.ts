/** The board's two palettes. */
export type Theme = 'light' | 'dark';

/** What the theme picker offers: follow the system, or pin one palette. Not persisted. */
export type ThemeChoice = 'system' | Theme;

/** The theme the operating system asks for, which the board follows by default. */
export function systemTheme(): Theme {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

/**
 * Call `onTheme` whenever the system theme changes, so the page can follow it
 * live; returns the matching unsubscribe.
 */
export function watchSystemTheme(onTheme: (theme: Theme) => void): () => void {
  const media = window.matchMedia('(prefers-color-scheme: dark)');
  const listener = () => onTheme(media.matches ? 'dark' : 'light');
  media.addEventListener('change', listener);
  return () => media.removeEventListener('change', listener);
}

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

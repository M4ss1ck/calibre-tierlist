/** The board's two themes; the toggle switches between them and persists nothing. */
export type Theme = 'light' | 'dark';

/** The theme the operating system asks for, which the board follows by default. */
export function systemTheme(): Theme {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

/**
 * Pin the theme for this session: `data-theme` on the root picks the colour
 * tokens, and its `color-scheme` rule makes the browser's own controls follow.
 */
export function applyTheme(theme: Theme): void {
  document.documentElement.dataset['theme'] = theme;
}

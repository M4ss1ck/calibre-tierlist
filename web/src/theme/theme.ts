/** The board's two themes; the toggle switches between them and persists nothing. */
export type Theme = 'light' | 'dark';

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
 * Show `theme`: `data-theme` on the root picks the colour tokens, and its
 * `color-scheme` rule makes the browser's own controls follow. Choosing the
 * theme the system already asks for removes the attribute instead, so the
 * board goes back to following the system.
 */
export function applyTheme(theme: Theme): void {
  const root = document.documentElement;
  if (theme === systemTheme()) delete root.dataset['theme'];
  else root.dataset['theme'] = theme;
}

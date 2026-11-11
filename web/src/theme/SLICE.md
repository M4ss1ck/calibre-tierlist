# SLICE: theme

## Purpose

Holds the board's colour tokens and the header toggle that switches between the light and dark theme. It is separate so every slice reads the same names instead of hard-coding a colour, and so the choice is made in one place.

## Public API

- `Theme`: `'light'` or `'dark'`; the only two themes, and the choice is not persisted.
- `systemTheme() -> Theme`: the theme the operating system asks for.
- `applyTheme(theme)`: pins the theme for the session by setting `data-theme` on the root element.
- Colour tokens on `:root`: `--bg`, `--fg`, `--muted`, `--border` (a frame), `--border-strong` (a control edge), `--scrim` (behind the Detail Panel), `--tier-ink` (text on a Tier colour), `--on-series` (text over a series gradient), and `--font-sans`.
- `:root` also carries `color-scheme`: light, or dark when the system asks or `data-theme="dark"` pins it, so form controls follow the theme.

## Files

- `theme.css`: the light tokens, the dark `prefers-color-scheme` block and the `[data-theme]` overrides; imported once by `src/main.ts`.
- `theme.ts`: the system preference lookup and the root pin.

## Depends on

- Ports: none.
- Slices: none; `board` and `filter` read the tokens, not the other way round.
- The browser DOM only (`matchMedia`, `documentElement`).

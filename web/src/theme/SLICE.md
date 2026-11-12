# SLICE: theme

## Purpose

Holds the board's colour tokens and the theme picker that chooses between following the system and pinning the light or dark palette. It is separate so every slice reads the same names instead of hard-coding a colour, and so the choice is made in one place. On System the board follows the operating system through CSS alone, including a live change of preference.

## Public API

- `Theme`: `'light'` or `'dark'`, the two palettes.
- `ThemeChoice`: `'system'` or a `Theme`; what the picker offers. Not persisted.
- `applyTheme(choice)`: `'light'` or `'dark'` sets `data-theme` on the root element, pinning that palette even when the system asks for the other; `'system'` removes the attribute so the `prefers-color-scheme` rules decide again.
- `ThemePicker(choice)`: a `role="group"` named "Theme" of three `aria-pressed` buttons, System, Light and Dark; `choice` is bindable, starts at `'system'`, and every change goes through `applyTheme`.
- Colour tokens on `:root`: `--bg`, `--fg`, `--muted`, `--border` (a frame), `--border-strong` (a control edge), `--surface` (a Lane's card well, a panel row), `--selected` (the pressed picker button), `--accent` and `--on-accent` (the switch), `--scrim` (behind a dialog), `--tier-ink` (text on a Tier colour), `--on-series` (text over a series colour), `--caption-bg` (the title box over a cover), and `--font-sans`.
- `:root` also carries `color-scheme`: light, or dark when the system asks (and nothing pins light) or `data-theme="dark"` pins it, so form controls follow the theme.

## Files

- `theme.css`: the light tokens, the dark `prefers-color-scheme` block and the `[data-theme='dark']` pin; imported once by `src/main.ts`.
- `theme.ts`: the `Theme` and `ThemeChoice` types and `applyTheme`.
- `ThemePicker.svelte`: the System / Light / Dark picker.

## Depends on

- Ports: none.
- Slices: none; `board` and `filter` read the tokens, not the other way round.
- The browser DOM only (`documentElement`).

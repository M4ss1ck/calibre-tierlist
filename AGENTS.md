# calibre-tierlist

Calibre 9.0+ plugin: assign books a customizable tier from the right-click menu, then compile a single offline, interactive HTML tier list of your series (exportable to PNG/PDF). Built 100% by agents.

## Layout

- `plugin/`: Python plugin (uv for dev only; zero runtime deps; runs in calibre's bundled Python).
- `web/`: Svelte 5 + TypeScript template, built into one `template.html` the plugin fills with data.
- `contract/tierlist.schema.json`: the single source of truth for the plugin-to-HTML data.

## Rules

- **Read narrowly.** Working in a slice: read its `SLICE.md` and `GLOSSARY.md`, nothing else, unless you touch another slice's public API.
- **Files stay short**: 150 lines hard cap, 100 soft, enforced by `just check`.
- **The core domain imports nothing from `calibre` or `qt`.** Only `calibre_ui` and port adapters do.
- **Every behavior change ships its test** in the same commit.
- **Specs and plans are GitHub issues**, never files. See `docs/agents/issue-tracker.md`.

## Agent skills

### Issue tracker

GitHub Issues on `M4ss1ck/calibre-tierlist`, via `gh`; specs are issues, plans are their sub-issues. See `docs/agents/issue-tracker.md`.

### Triage labels

The five default roles (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: root `GLOSSARY.md` + `docs/adr/`, plus a `SLICE.md` brief per slice. See `docs/agents/domain.md`.

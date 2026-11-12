# SLICE: board

## Purpose

Draws the compiled Tier List as a Sheet: an editable title, Lanes of Stacks and Cards (one Lane per Tier in config order, then the Unranked Lane) and a footer, plus the Series Panel and Detail Panel dialogs. It is separate so rendering stays a pure function of Tier List Data and the reader's page-only choices.

## Public API

- `App(data)`: the whole page. A `.sheet` wraps the `SheetHeader`, the `.controls` toolbar (View: `UnrankedSwitch` and the `theme` slice's `ThemePicker`; Export: the `export` slice's buttons, handed the sheet element), the `FilterBar` whose `Filters` it holds, the `.lanes` and the footer. It keeps the renamed title and Lane labels (by Tier id, or `unranked`) for the session, so a label survives the Unranked Lane being switched off and on. Outside the sheet it mounts the `SeriesPanel` for the opened Stack and the `Detail` for the last pick.
- `SheetHeader(data, title)`: the editable `h1` title (bindable, default "Tier List", mirrored to `document.title`) and a line with the book count, series count and library name.
- `UnrankedSwitch(on)`: a `role="switch"` button labelled "Unranked lane", `aria-checked` bound to `on`; its visible label toggles it too.
- `Lane(lane, label, colour, books, covers, series, filters, onopen, onrename)`: one Lane as a `section` whose `aria-label` is the shown label and whose `data-lane-id` is the Tier id or `unranked`. A full-height label cell in the Tier colour holds the editable `h2` (smaller when longer than three characters); it draws `laneEntries`, so its Stacks and Cards stay interleaved in Lane Order. Only Cards whose book `matchesBook` and Stacks whose series `matchesSeries` (over the series' books) are drawn; the Lane itself stays even when empty.
- `laneEntries(lane, books, covers, series, filters) -> LaneEntry[]`: the Lane's items that survive the Board Filter, in Lane Order; each `LaneEntry` is a `stack` with its name and `Series`, or a `card` with its id, `Book` and cover. References the payload does not hold are skipped.
- `Stack(name, series, books, covers, onopen)`: a `figure` named after the series with one front button, named "<series>, N of M books", that calls `onopen({ stack: name })`. The front shows the cover `frontOf` picks (dimmed when that book is unread) or the series colour, a `.count` "owned/total" badge and a `.name` box, with up to two `.behind` sheets and the Override badge.
- `SeriesPanel(name, series, books, covers, tiers, onpick, onclose)`: a modal `dialog.series-panel` named after the series, with a "N of M books in your library" summary and one row per position, cut ones included; a row shows `#number`, the title or "Not in your library", and the Book Tier (or "Unranked"). Picking a row closes it and passes the `Selection` up; Escape or Close returns focus to the Stack.
- `Card(title, cover, onopen)`: one book's cover with its title in a box over the bottom; `cover` is its Cover or undefined for the Placeholder style.
- `Detail(selection, tiers, onclose)`: the Detail Panel, a modal `dialog.detail` for a `Selection` (a `Book`, or a Placeholder's series and number).
- `stack.ts`: `StackPick`, `Resolved`, `resolve(series, books, covers)` (every position with its book and cover), `frontOf(resolved)` (first owned book with a cover, else first owned book, else first position) and `sheetsBehind(resolved)` (one per other position, at most two).
- `editable.ts`: `cleanText(text)` (collapses whitespace runs, trims) and the `editable(node, { value, onchange })` action: plain-text contenteditable where Enter or leaving commits the cleaned text, Escape reverts, and an empty edit falls back to the value it had.

## Files

- `SheetHeader.svelte`, `UnrankedSwitch.svelte`, `Lane.svelte`, `Stack.svelte`, `SeriesPanel.svelte`, `Card.svelte`, `Detail.svelte`: the components above.
- `OverrideMark.svelte`: the Override badge (top corner) on a Stack whose Series Tier is an Override, which also carries `data-override="true"`.
- `lane.ts`: `LaneEntry` and `laneEntries`, the Board Filter applied to a Lane's interleaved items; unit tested in `lane.test.ts`.
- `stack.ts`, `editable.ts`: the pure Stack helpers and the rename action, unit tested in `stack.test.ts` and `editable.test.ts`.

## Depends on

- Ports: none; it draws the Tier List Data passed as props.
- Slices: `contract` for `TierListData`, `Tier`, `Lane`, `Book`, `Series`, `Position`, and `Cover` types; `filter` for the `Filters` type and its predicates (App also mounts `FilterBar`); `theme` for the colour tokens and `ThemePicker`; `export` for `ExportButton` and `PdfButton`. The `export` slice reads the `.sheet`, `.controls`, `.lanes`, Lanes' `data-lane-id` and, in `print.css`, the `.stack`, `.card`, `dialog.series-panel` and `dialog.detail` markup.
- Svelte only; no calibre or network access.

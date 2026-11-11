# SLICE: filter

## Purpose

Decides whether a book or a whole Stack survives the board's filters. It is separate so the filtering is a pure, testable function of Tier List Data, with no UI or DOM.

## Public API

- `Filters`: the active criteria; a non-empty `query`, plus an optional exact `author`, exact `tag` and Read State `year`.
- `matchesBook(book, filters) -> boolean`: every set criterion must hold (AND); the query is trimmed, case-insensitive and matches the title, any author or the series name.
- `matchesSeries(name, books, filters) -> boolean`: a Stack stays visible when the series name answers the query and a book answers the other criteria, or when any of its books matches.
- `filterOptions(books) -> FilterOptions`: sorted unique authors and tags, and the Read State years present, newest first.
- `hasReadYears(books) -> boolean`: false when no book has a Read State date, so the UI hides the year filter.
- `FilterBar(books, filters)`: the search box and the Author, Tag and Year read selects, each with an "All" choice; options come from `filterOptions(Object.values(books))`. It drops the Year read select and shows a muted note when `hasReadYears(books)` is false. `filters` is bindable (`bind:filters`).

## Files

- `filter.ts`: the predicates and the options derived from the books.
- `FilterBar.svelte`: the filter controls, writing their values into the bound `filters`.

## Depends on

- Ports: none.
- Slices: `contract` for the `Book` type.
- Svelte and the DOM are not involved.

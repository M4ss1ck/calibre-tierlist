<script lang="ts">
  import type { Book } from '../contract/tierlist';
  import { filterOptions, hasReadYears, type Filters } from './filter';

  type Props = { books: Record<string, Book>; filters: Filters };
  let { books, filters = $bindable() }: Props = $props();

  const all = $derived(Object.values(books));
  const options = $derived(filterOptions(all));
  const years = $derived(hasReadYears(all));
</script>

<form class="filters" role="search" onsubmit={(event) => event.preventDefault()}>
  <label class="field">
    <span class="caption">Search</span>
    <input type="search" placeholder="Title, author or series" bind:value={filters.query} />
  </label>
  <label class="field">
    <span class="caption">Author</span>
    <select bind:value={filters.author}>
      <option value={null}>All</option>
      {#each options.authors as author (author)}
        <option value={author}>{author}</option>
      {/each}
    </select>
  </label>
  <label class="field">
    <span class="caption">Tag</span>
    <select bind:value={filters.tag}>
      <option value={null}>All</option>
      {#each options.tags as tag (tag)}
        <option value={tag}>{tag}</option>
      {/each}
    </select>
  </label>
  {#if years}
    <label class="field">
      <span class="caption">Year read</span>
      <select bind:value={filters.year}>
        <option value={null}>All</option>
        {#each options.years as year (year)}
          <option value={year}>{year}</option>
        {/each}
      </select>
    </label>
  {:else}
    <p class="note">Year filter unavailable: the read column has no dates.</p>
  {/if}
</form>

<style>
  .filters {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    gap: 0.75rem;
    margin: 0;
    padding: 0.75rem;
    border: 1px solid var(--border);
    border-radius: 0.75rem;
    background: var(--surface);
  }

  .field {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    max-width: 100%;
    min-width: 0;
  }

  .field:first-child {
    flex: 1 1 14rem;
  }

  .caption {
    color: var(--muted);
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  input,
  select {
    box-sizing: border-box;
    max-width: 100%;
    height: 2.5rem;
    padding: 0 0.625rem;
    border: 1px solid var(--border-strong);
    border-radius: 0.5rem;
    background: var(--bg);
    color: var(--fg);
    font: inherit;
    font-size: 0.875rem;
  }

  input:focus-visible,
  select:focus-visible {
    outline: 2px solid var(--fg);
    outline-offset: 2px;
  }

  .note {
    margin: 0 0 0.5rem;
    color: var(--muted);
    font-size: 0.85rem;
  }
</style>

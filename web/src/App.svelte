<script lang="ts">
  import Detail, { type Selection } from './board/Detail.svelte';
  import Lane from './board/Lane.svelte';
  import type { TierListData } from './contract/tierlist';
  import ExportButton from './export/ExportButton.svelte';
  import type { Filters } from './filter/filter';
  import FilterBar from './filter/FilterBar.svelte';
  import { applyTheme, systemTheme, watchSystemTheme, type Theme } from './theme/theme';

  let { data }: { data: TierListData } = $props();
  let board = $state<HTMLElement>();
  let selection = $state<Selection | undefined>();
  let unranked = $state(true);
  let systemDark = $state(systemTheme() === 'dark');
  /** The theme the toggle chose, or null while the board follows the system. */
  let pinned = $state<Theme | null>(null);
  let filters = $state<Filters>({ query: '', author: null, tag: null, year: null });
  const lanes = $derived(data.lanes.filter((lane) => unranked || lane.tier !== null));
  const dark = $derived(pinned === null ? systemDark : pinned === 'dark');

  $effect(() => watchSystemTheme((theme) => (systemDark = theme === 'dark')));

  function toggleTheme() {
    const next: Theme = dark ? 'light' : 'dark';
    applyTheme(next);
    pinned = next === systemTheme() ? null : next;
  }
</script>

<main class="board">
  <header>
    <h1>Tier List</h1>
    <div class="actions">
      <button type="button" class="toggle" aria-pressed={unranked} onclick={() => (unranked = !unranked)}>
        Unranked Lane
      </button>
      <button type="button" class="toggle" aria-pressed={dark} onclick={toggleTheme}>Dark theme</button>
      <ExportButton {board} />
    </div>
  </header>
  <FilterBar books={data.books} bind:filters />
  <div class="lanes" bind:this={board}>
    {#each lanes as lane (lane.tier ?? 'unranked')}
      <Lane
        {lane}
        tiers={data.tiers}
        books={data.books}
        covers={data.covers}
        series={data.series}
        {filters}
        onopen={(picked) => (selection = picked)}
      />
    {/each}
  </div>
  <Detail {selection} tiers={data.tiers} onclose={() => (selection = undefined)} />
</main>

<style>
  :global(body) {
    margin: 0;
    min-height: 100vh;
    background: var(--bg);
    color: var(--fg);
    font-family: var(--font-sans);
    line-height: 1.5;
  }

  .board {
    max-width: 60rem;
    margin: 0 auto;
    padding: 2rem 1rem;
  }

  header {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem 1rem;
    margin: 0 0 1.5rem;
  }

  h1 {
    margin: 0;
    font-size: 1.75rem;
    letter-spacing: 0.01em;
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    gap: 0.5rem;
    margin-left: auto;
  }

  .lanes {
    display: flow-root;
  }

  .toggle {
    padding: 0.2rem 0.6rem;
    border: 1px solid var(--border-strong);
    border-radius: 999px;
    background: none;
    color: var(--muted);
    font: inherit;
    font-size: 0.85rem;
    cursor: pointer;
  }

  .toggle[aria-pressed='true'] {
    background: color-mix(in srgb, var(--fg) 12%, var(--bg));
    color: var(--fg);
  }

  .toggle:focus-visible {
    outline: 2px solid var(--fg);
    outline-offset: 2px;
  }

  @media (max-width: 480px) {
    .board {
      padding: 1.25rem 0.75rem;
    }

    h1 {
      font-size: 1.5rem;
    }
  }
</style>

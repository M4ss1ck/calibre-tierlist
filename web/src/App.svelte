<script lang="ts">
  import Detail, { type Selection } from './board/Detail.svelte';
  import Lane from './board/Lane.svelte';
  import type { TierListData } from './contract/tierlist';

  let { data }: { data: TierListData } = $props();
  let selection = $state<Selection | undefined>();
  let unranked = $state(true);
  const lanes = $derived(data.lanes.filter((lane) => unranked || lane.tier !== null));
</script>

<main class="board">
  <header>
    <h1>Tier List</h1>
    <button type="button" class="toggle" aria-pressed={unranked} onclick={() => (unranked = !unranked)}>
      Unranked Lane
    </button>
  </header>
  {#each lanes as lane (lane.tier ?? 'unranked')}
    <Lane
      {lane}
      tiers={data.tiers}
      books={data.books}
      covers={data.covers}
      series={data.series}
      onopen={(picked) => (selection = picked)}
    />
  {/each}
  <Detail {selection} tiers={data.tiers} onclose={() => (selection = undefined)} />
</main>

<style>
  :global(:root) {
    --bg: #f7f7f8;
    --fg: #1b1b1f;
    --muted: #5b5b66;
    --font-sans:
      system-ui, -apple-system, 'Segoe UI', roboto, 'Helvetica Neue', arial,
      sans-serif;

    color-scheme: light dark;
  }

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
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin: 0 0 1.5rem;
  }

  h1 {
    margin: 0;
    font-size: 1.75rem;
    letter-spacing: 0.01em;
  }

  .toggle {
    padding: 0.2rem 0.6rem;
    border: 1px solid color-mix(in srgb, var(--fg) 30%, var(--bg));
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

  @media (prefers-color-scheme: dark) {
    :global(:root) {
      --bg: #121214;
      --fg: #f4f4f5;
      --muted: #a1a1aa;
    }
  }
</style>

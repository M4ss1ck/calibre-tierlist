<script lang="ts">
  import Lane from './board/Lane.svelte';
  import type { TierListData } from './contract/tierlist';

  let { data }: { data: TierListData } = $props();
</script>

<main class="board">
  <h1>Tier List</h1>
  {#each data.lanes as lane (lane.tier ?? 'unranked')}
    <Lane
      {lane}
      tiers={data.tiers}
      books={data.books}
      covers={data.covers}
      series={data.series}
    />
  {/each}
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

  h1 {
    margin: 0 0 1.5rem;
    font-size: 1.75rem;
    letter-spacing: 0.01em;
  }

  @media (prefers-color-scheme: dark) {
    :global(:root) {
      --bg: #121214;
      --fg: #f4f4f5;
      --muted: #a1a1aa;
    }
  }
</style>

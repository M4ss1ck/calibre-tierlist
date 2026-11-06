<script lang="ts">
  import type { Book, Lane, Tier } from '../contract/tierlist';
  import Card from './Card.svelte';

  let {
    lane,
    tiers,
    books,
  }: { lane: Lane; tiers: Tier[]; books: Record<string, Book> } = $props();

  const tier = $derived(
    lane.tier === null ? undefined : tiers.find((candidate) => candidate.id === lane.tier),
  );
  const label = $derived(tier?.label ?? 'Unranked');
  const colour = $derived(tier?.colour ?? '#8a8a94');
  const cards = $derived(
    lane.cards.flatMap((id) => {
      const book = books[id];
      return book ? [{ id, title: book.title }] : [];
    }),
  );
</script>

<section class="lane" aria-label={label}>
  <h2 class="label" style:background-color={colour}>{label}</h2>
  <div class="cards">
    {#each cards as card (card.id)}
      <Card title={card.title} />
    {/each}
  </div>
</section>

<style>
  .lane {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
  }

  .label {
    flex: 0 0 4.5rem;
    margin: 0;
    padding: 0.5rem 0;
    border-radius: 0.375rem;
    color: #1b1b1f;
    font-size: 1rem;
    text-align: center;
  }

  .cards {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    flex: 1 1 auto;
    min-height: 2.5rem;
  }
</style>

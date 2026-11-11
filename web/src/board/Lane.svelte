<script lang="ts">
  import type { Book, Cover, Lane, Series, Tier } from '../contract/tierlist';
  import type { Filters } from '../filter/filter';
  import { matchesBook, matchesSeries } from '../filter/filter';
  import Card from './Card.svelte';
  import type { Selection } from './Detail.svelte';
  import Stack from './Stack.svelte';

  let {
    lane,
    tiers,
    books,
    covers,
    series,
    filters,
    onopen,
  }: {
    lane: Lane;
    tiers: Tier[];
    books: Record<string, Book>;
    covers: Record<string, Cover>;
    series: Record<string, Series>;
    filters: Filters;
    onopen: (selection: Selection) => void;
  } = $props();

  const tier = $derived(
    lane.tier === null ? undefined : tiers.find((candidate) => candidate.id === lane.tier),
  );
  const label = $derived(tier?.label ?? 'Unranked');
  const colour = $derived(tier?.colour ?? '#8a8a94');
  const cards = $derived(
    lane.cards.flatMap((id) => {
      const book = books[id];
      return book && matchesBook(book, filters) ? [{ id, book, cover: covers[id] }] : [];
    }),
  );
  const stacks = $derived(
    lane.stacks.flatMap((name) => {
      const entry = series[name];
      if (!entry) return [];
      const owned = entry.positions.flatMap((position) => {
        const book = position.book === null ? undefined : books[position.book];
        return book ? [book] : [];
      });
      return matchesSeries(name, owned, filters) ? [{ name, series: entry }] : [];
    }),
  );
</script>

<section class="lane" aria-label={label} data-lane-id={lane.tier ?? 'unranked'}>
  <h2 class="label" style:background-color={colour}>{label}</h2>
  <div class="cards">
    {#each stacks as stack (stack.name)}
      <Stack
        name={stack.name}
        series={stack.series}
        {books}
        {covers}
        {tiers}
        {onopen}
      />
    {/each}
    {#each cards as card (card.id)}
      <Card title={card.book.title} cover={card.cover} onopen={() => onopen({ book: card.book })} />
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
    color: var(--tier-ink);
    font-size: 1rem;
    text-align: center;
  }

  .cards {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    flex: 1 1 auto;
    min-width: 0;
    min-height: 2.5rem;
  }

  @media (max-width: 480px) {
    .lane {
      gap: 0.5rem;
    }
  }
</style>

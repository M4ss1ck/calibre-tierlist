<script lang="ts">
  import type { Book, Cover, Series, Tier } from '../contract/tierlist';
  import type { Selection } from './Detail.svelte';
  import OverrideMark from './OverrideMark.svelte';
  import Position from './Position.svelte';

  type Props = {
    name: string;
    series: Series;
    books: Record<string, Book>;
    covers: Record<string, Cover>;
    tiers: Tier[];
    onopen: (selection: Selection) => void;
  };

  let { name, series, books, covers, tiers, onopen }: Props = $props();
  let expanded = $state(false);

  const all = $derived(
    series.positions.map((position) => {
      const book = position.book === null ? undefined : books[position.book];
      const tier = tiers.find((candidate) => candidate.id === (book?.tier ?? ''));
      return {
        number: position.number,
        book,
        cover: position.book === null ? undefined : covers[position.book],
        label: tier?.label ?? '-',
        colour: tier?.colour ?? '#8a8a94',
      };
    }),
  );
  const shown = $derived(expanded ? all : all.slice(0, all.length - series.more));
  const owned = $derived(shown.filter((position) => position.book !== undefined));
  const gradient = $derived(
    `linear-gradient(160deg, ${series.colour}, color-mix(in srgb, ${series.colour} 45%, #000))`,
  );
</script>

<figure class="stack" aria-label={name} data-override={series.override ? 'true' : undefined}>
  <div class="positions" class:expanded>
    {#each shown as position, index (index)}
      <Position
        {name}
        number={position.number}
        book={position.book}
        cover={position.cover}
        background={gradient}
        layer={shown.length - index}
        onopen={() =>
          onopen(position.book ? { book: position.book } : { series: name, number: position.number })}
      />
    {/each}
    {#if series.more > 0 && !expanded}
      <span class="more">+{series.more}</span>
    {/if}
    {#if series.override}
      <OverrideMark />
    {/if}
  </div>
  <div class="badges">
    {#each owned as position, index (index)}
      <span class="tier-badge" style:background-color={position.colour}>{position.label}</span>
    {/each}
    {#if series.more > 0}
      <button type="button" class="toggle" aria-expanded={expanded} onclick={() => (expanded = !expanded)}>
        {expanded ? 'Show fewer' : `Show all ${all.length}`}
      </button>
    {/if}
  </div>
</figure>

<style>
  .stack { display: flex; flex-direction: column; gap: 0.3rem; margin: 0; }
  .positions { position: relative; display: flex; align-items: flex-start; }
  .positions:not(.expanded) > :global(.position + .position) { margin-left: -3.5rem; }
  .positions.expanded { flex-wrap: wrap; gap: 0.5rem; }
  .more {
    position: absolute; right: 0.25rem; bottom: 0.25rem; z-index: 99; padding: 0 0.35rem;
    border: 1px solid var(--bg); border-radius: 999px; color: var(--bg); font-size: 0.7rem;
    background: color-mix(in srgb, var(--fg) 82%, var(--bg)); line-height: 1.5;
  }
  .badges { display: flex; flex-wrap: wrap; align-items: center; gap: 0.25rem; }
  .tier-badge {
    padding: 0 0.35rem; border-radius: 0.25rem; color: #1b1b1f; font-size: 0.7rem; line-height: 1.5;
  }
  .toggle {
    margin-left: auto; padding: 0 0.4rem; border: 1px solid color-mix(in srgb, var(--fg) 30%, var(--bg));
    border-radius: 999px; background: none; color: var(--fg); font: inherit; font-size: 0.7rem;
    line-height: 1.5; cursor: pointer;
  }
  .toggle:focus-visible { outline: 2px solid var(--fg); outline-offset: 2px; }
</style>

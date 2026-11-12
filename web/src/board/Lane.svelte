<script lang="ts">
  import type { Book, Cover, Lane, Series } from '../contract/tierlist';
  import type { Filters } from '../filter/filter';
  import Card from './Card.svelte';
  import type { Selection } from './Detail.svelte';
  import { editable } from './editable';
  import { laneEntries } from './lane';
  import Stack from './Stack.svelte';
  import type { StackPick } from './stack';

  type Props = {
    lane: Lane;
    label: string;
    colour: string;
    description: string | null;
    emptyMessage: string | null;
    showLabel: boolean;
    showCaption: boolean;
    showReadCount: boolean;
    books: Record<string, Book>;
    covers: Record<string, Cover>;
    series: Record<string, Series>;
    /** Each series' session Series Cover pick, by series name. */
    fronts: Record<string, string>;
    filters: Filters;
    onopen: (opened: Selection | StackPick) => void;
    onrename: (label: string) => void;
  };
  let {
    lane,
    label,
    colour,
    description,
    emptyMessage,
    showLabel,
    showCaption,
    showReadCount,
    books,
    covers,
    series,
    fronts,
    filters,
    onopen,
    onrename,
  }: Props = $props();

  const entries = $derived(laneEntries(lane, books, covers, series, filters));
  const long = $derived(label.length > 3);
</script>

<section class="lane" aria-label={label} data-lane-id={lane.tier ?? 'unranked'}>
  <div class="label" style:background-color={colour}>
    {#if showLabel}
      <h2 class:long title="Click to rename" use:editable={{ value: label, onchange: onrename }}></h2>
    {/if}
    {#if description}
      <p class="description">{description}</p>
    {/if}
  </div>
  <div class="cards">
    {#each entries as entry (entry.kind === 'stack' ? `stack:${entry.name}` : `card:${entry.id}`)}
      {#if entry.kind === 'stack'}
        <Stack
          name={entry.name}
          series={entry.series}
          chosen={fronts[entry.name]}
          {showCaption}
          {showReadCount}
          {books}
          {covers}
          {onopen}
        />
      {:else}
        <Card title={entry.book.title} {showCaption} cover={entry.cover} onopen={() => onopen({ book: entry.book })} />
      {/if}
    {/each}
    {#if entries.length === 0 && emptyMessage !== null}
      <p class="empty">{emptyMessage}</p>
    {/if}
  </div>
</section>

<style>
  .lane { display: flex; min-height: 12.5rem; }
  .lane:not(:first-child) { border-top: 1px solid var(--border); }
  .label {
    display: flex; flex: 0 0 7rem; flex-direction: column; gap: 0.25rem;
    align-items: center; justify-content: center; box-sizing: border-box; padding: 0.625rem;
  }
  h2 {
    box-sizing: border-box; width: 100%; margin: 0; padding: 0.375rem 0.125rem;
    border: 1px dashed transparent; border-radius: 0.5rem; color: var(--tier-ink);
    font-size: 2rem; font-weight: 700; line-height: 1.15; text-align: center;
    overflow-wrap: anywhere; cursor: text;
  }
  h2.long { font-size: 1rem; }
  h2:hover { border-color: color-mix(in srgb, var(--tier-ink) 40%, transparent); }
  h2:focus {
    outline: 2px solid var(--tier-ink); outline-offset: 1px; background: rgb(255 255 255 / 40%);
  }
  .description {
    margin: 0; color: var(--tier-ink); font-size: 0.75rem; line-height: 1.3;
    text-align: center; overflow-wrap: anywhere;
  }
  .cards {
    display: flex; flex: 1 1 auto; flex-wrap: wrap; align-content: flex-start; align-items: flex-start;
    gap: var(--cover-gap-y, 0.875rem) var(--cover-gap-x, 1.375rem);
    min-width: 0; padding: 0.75rem 1.125rem 0.875rem; background: var(--surface);
  }
  .empty { align-self: center; margin: 0; color: var(--muted); }
  @media (max-width: 480px) {
    .label { flex-basis: 5.25rem; padding: 0.375rem; }
    h2 { font-size: 1.5rem; }
    h2.long { font-size: 0.8rem; }
    .cards {
      gap: min(var(--cover-gap-y, 0.875rem), 0.75rem) min(var(--cover-gap-x, 1.375rem), 0.75rem);
      padding: 0.625rem;
    }
  }
</style>

<script lang="ts">
  import type { Book, Cover, Series, Tier } from '../contract/tierlist';
  import type { Selection } from './Detail.svelte';
  import { resolve } from './stack';

  type Props = {
    name: string | undefined;
    series: Series | undefined;
    books: Record<string, Book>;
    covers: Record<string, Cover>;
    tiers: Tier[];
    onpick: (selection: Selection) => void;
    onclose: () => void;
  };
  let { name, series, books, covers, tiers, onpick, onclose }: Props = $props();
  let dialog: HTMLDialogElement;

  const rows = $derived(
    series && name
      ? resolve(series, books, covers).map(({ position, book }) => ({
          number: position.number,
          book,
          tier: book ? tiers.find((candidate) => candidate.id === book.tier) : undefined,
          pick: (): Selection => (book ? { book } : { series: name, number: position.number }),
        }))
      : [],
  );
  const owned = $derived(rows.filter((row) => row.book !== undefined).length);

  $effect(() => {
    if (name && !dialog.open) dialog.showModal();
  });

  function choose(selection: Selection) {
    dialog.close();
    onpick(selection);
  }
</script>

<dialog class="series-panel" bind:this={dialog} aria-labelledby="series-title" onclose={onclose}>
  {#if name}
    <header>
      <div>
        <h2 id="series-title">{name}</h2>
        <p class="summary">{owned} of {rows.length} books in your library</p>
      </div>
      <button type="button" class="close" aria-label="Close" onclick={() => dialog.close()}>×</button>
    </header>
    <ol>
      {#each rows as row, index (index)}
        <li>
          <button type="button" class="row" class:missing={!row.book} onclick={() => choose(row.pick())}>
            <span class="number">#{row.number}</span>
            <span class="title">{row.book?.title ?? 'Not in your library'}</span>
            {#if row.tier}
              <span class="tier" style:background-color={row.tier.colour}>{row.tier.label}</span>
            {:else if row.book}
              <span class="tier unranked">Unranked</span>
            {/if}
          </button>
        </li>
      {/each}
    </ol>
  {/if}
</dialog>

<style>
  .series-panel {
    box-sizing: border-box;
    width: min(30rem, calc(100vw - 2rem));
    padding: 1.25rem;
    border: 1px solid var(--border);
    border-radius: 0.5rem;
    background: var(--bg);
    color: var(--fg);
  }
  .series-panel::backdrop { background: var(--scrim); }
  header { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; }
  h2 { margin: 0; font-size: 1.25rem; overflow-wrap: anywhere; }
  .summary { margin: 0.25rem 0 0.75rem; color: var(--muted); font-size: 0.85rem; }
  .close {
    padding: 0 0.5rem; border: 0; border-radius: 0.25rem; background: transparent;
    color: var(--muted); font-size: 1.5rem; line-height: 1; cursor: pointer;
  }
  .close:hover, .close:focus-visible { color: var(--fg); }
  ol { display: flex; flex-direction: column; gap: 0.25rem; margin: 0; padding: 0; list-style: none; }
  .row {
    display: flex; align-items: center; gap: 0.75rem; width: 100%; min-height: 2.75rem;
    padding: 0 0.625rem; border: 1px solid var(--border); border-radius: 0.375rem;
    background: var(--surface); color: var(--fg); font: inherit; text-align: start; cursor: pointer;
  }
  .row:focus-visible { outline: 2px solid var(--fg); outline-offset: 1px; }
  .row.missing { color: var(--muted); border-style: dashed; background: transparent; }
  .number { flex: none; min-width: 2.5rem; color: var(--muted); font-size: 0.85rem; }
  .title { flex: 1; min-width: 0; overflow-wrap: anywhere; }
  .tier {
    flex: none; padding: 0 0.45rem; border-radius: 0.25rem;
    color: var(--tier-ink); font-size: 0.8rem; font-weight: 600;
  }
  .tier.unranked { color: var(--muted); border: 1px solid var(--border-strong); }
</style>

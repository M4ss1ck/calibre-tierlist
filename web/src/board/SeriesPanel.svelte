<script lang="ts">
  import type { Book, Cover, Series, Tier } from '../contract/tierlist';
  import type { Selection } from './Detail.svelte';
  import type { ReturnTo } from './dialogs';
  import SeriesRow from './SeriesRow.svelte';
  import { canFront, frontOf, pickFront, resolve } from './stack';

  type Props = {
    name: string | undefined;
    series: Series | undefined;
    books: Record<string, Book>;
    covers: Record<string, Cover>;
    tiers: Tier[];
    /** The book id picked as this series' Series Cover for the session, if any. */
    chosen: string | undefined;
    /** The row whose title takes focus when the panel opens, after a back from Detail. */
    focusRow: number | undefined;
    onpick: (selection: Selection, from: ReturnTo) => void;
    onfront: (name: string, chosen: string | undefined) => void;
    onclose: () => void;
  };
  let { name, series, books, covers, tiers, chosen, focusRow, onpick, onfront, onclose }: Props = $props();
  let dialog: HTMLDialogElement;

  const resolved = $derived(series && name ? resolve(series, books, covers) : []);
  const front = $derived(frontOf(resolved, chosen)?.position.book);
  const rows = $derived(
    resolved.map((entry) => ({
      number: entry.position.number,
      id: entry.position.book,
      book: entry.book,
      tier: entry.book ? tiers.find((candidate) => candidate.id === entry.book?.tier) : undefined,
      eligible: canFront(entry),
    })),
  );
  const owned = $derived(rows.filter((row) => row.book !== undefined).length);

  $effect(() => {
    if (!name) {
      if (dialog.open) dialog.close();
      return;
    }
    if (dialog.open) return;
    dialog.showModal();
    if (focusRow !== undefined) dialog.querySelectorAll<HTMLElement>('button.title')[focusRow]?.focus();
  });

  function choose(selection: Selection, series: string, row: number) {
    dialog.close();
    onpick(selection, { series, row });
  }

  function selectionOf(row: (typeof rows)[number], series: string): Selection {
    return row.book ? { book: row.book } : { series, number: row.number };
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
        <SeriesRow
          number={row.number}
          book={row.book}
          tier={row.tier}
          eligible={row.eligible}
          front={row.eligible && row.id === front}
          onopen={() => name && choose(selectionOf(row, name), name, index)}
          onfront={() => name && row.id !== null && onfront(name, pickFront(resolved, chosen, row.id))}
        />
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
</style>

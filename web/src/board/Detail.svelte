<script module lang="ts">
  import type { Book } from '../contract/tierlist';

  /** What the detail panel shows: an owned book, or a Placeholder's series position. */
  export type Selection = { book: Book } | { series: string; number: string };
</script>

<script lang="ts">
  import type { Tier } from '../contract/tierlist';

  type Props = { selection: Selection | undefined; tiers: Tier[]; onclose: () => void };
  let { selection, tiers, onclose }: Props = $props();
  let dialog: HTMLDialogElement;

  const book = $derived(selection && 'book' in selection ? selection.book : undefined);
  const series = $derived(
    book ? book.series : selection && 'series' in selection ? selection.series : null,
  );
  const number = $derived(
    book ? book.seriesIndex : selection && 'number' in selection ? selection.number : null,
  );
  const tier = $derived(book ? tiers.find((candidate) => candidate.id === book.tier) : undefined);
  const heading = $derived(book?.title ?? `${series ?? ''} #${number ?? ''}`);

  $effect(() => {
    if (selection && !dialog.open) dialog.showModal();
  });
</script>

<dialog class="detail" bind:this={dialog} aria-labelledby="detail-title" onclose={onclose}>
  {#if selection}
    <header>
      <h2 id="detail-title">{heading}</h2>
      <button type="button" class="close" aria-label="Close" onclick={() => dialog.close()}>×</button>
    </header>
    <dl>
      {#if book && book.authors.length > 0}
        <dt>Authors</dt><dd class="authors">{book.authors.join(', ')}</dd>
      {/if}
      {#if series}
        <dt>Series</dt><dd class="series">{series}{number ? ` #${number}` : ''}</dd>
      {/if}
      {#if !book}
        <dt>Library</dt><dd class="library">Not in your library</dd>
      {/if}
      {#if tier}
        <dt>Tier</dt>
        <dd class="tier"><span class="badge" style:background-color={tier.colour}>{tier.label}</span></dd>
      {:else if book}
        <dt>Tier</dt><dd class="tier">Unranked</dd>
      {/if}
      {#if book}
        <dt>Read</dt><dd class="read">{book.dateRead ?? (book.read ? 'Yes' : 'Not yet')}</dd>
      {/if}
      {#if book && book.rating !== null}
        <dt>Rating</dt><dd class="rating">{book.rating} / 5</dd>
      {/if}
      {#if book && book.tags.length > 0}
        <dt>Tags</dt><dd class="tags">{book.tags.join(', ')}</dd>
      {/if}
    </dl>
    {#if book?.blurb}
      <p class="blurb">{book.blurb}</p>
    {/if}
  {/if}
</dialog>

<style>
  .detail {
    width: min(32rem, calc(100vw - 2rem));
    padding: 1.25rem;
    border: 1px solid color-mix(in srgb, var(--fg) 18%, var(--bg));
    border-radius: 0.5rem;
    background: var(--bg);
    color: var(--fg);
  }
  .detail::backdrop { background: rgb(0 0 0 / 45%); }
  header { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; }
  h2 { margin: 0 0 0.75rem; font-size: 1.25rem; }
  .close {
    padding: 0 0.5rem; border: 0; border-radius: 0.25rem; background: transparent;
    color: var(--muted); font-size: 1.5rem; line-height: 1; cursor: pointer;
  }
  .close:hover, .close:focus-visible { color: var(--fg); }
  dl { display: grid; grid-template-columns: auto 1fr; gap: 0.25rem 1rem; margin: 0; }
  dt { color: var(--muted); font-size: 0.85rem; }
  dd { margin: 0; }
  .badge { padding: 0 0.4rem; border-radius: 0.25rem; color: #1b1b1f; font-size: 0.8rem; }
  .blurb { margin: 1rem 0 0; white-space: pre-line; }
</style>

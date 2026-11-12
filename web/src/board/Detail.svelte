<script module lang="ts">
  import type { Book } from '../contract/tierlist';

  /** What the detail panel shows: an owned book, or a Placeholder's series position. */
  export type Selection = { book: Book } | { series: string; number: string };
</script>

<script lang="ts">
  import type { Tier } from '../contract/tierlist';

  type Props = {
    selection: Selection | undefined;
    tiers: Tier[];
    /** The series whose panel the back button reopens, when Detail was opened from one. */
    back: string | undefined;
    onback: () => void;
    onclose: () => void;
  };
  let { selection, tiers, back, onback, onclose }: Props = $props();
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
    else if (!selection && dialog.open) dialog.close();
  });
</script>

<dialog class="detail" bind:this={dialog} aria-labelledby="detail-title" onclose={onclose}>
  {#if selection}
    <header>
      {#if back !== undefined}
        <button
          type="button"
          class="back"
          aria-label={`Back to ${back}`}
          title={`Back to ${back}`}
          onclick={() => {
            dialog.close();
            onback();
          }}>‹</button
        >
      {/if}
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
    box-sizing: border-box;
    width: min(32rem, calc(100vw - 2rem));
    max-width: calc(100vw - 2rem);
    padding: 1.25rem;
    border: 1px solid var(--border);
    border-radius: 0.5rem;
    background: var(--bg);
    color: var(--fg);
  }
  .detail::backdrop { background: var(--scrim); }
  header { display: flex; align-items: flex-start; gap: 0.5rem; }
  h2 { flex: 1; margin: 0 0 0.75rem; font-size: 1.25rem; overflow-wrap: anywhere; }
  .back, .close {
    padding: 0 0.5rem; border: 0; border-radius: 0.25rem; background: transparent;
    color: var(--muted); font-size: 1.5rem; line-height: 1; cursor: pointer;
  }
  .back { margin-left: -0.5rem; }
  .back:hover, .back:focus-visible, .close:hover, .close:focus-visible { color: var(--fg); }
  dl { display: grid; grid-template-columns: auto 1fr; gap: 0.25rem 1rem; margin: 0; }
  dt { color: var(--muted); font-size: 0.85rem; }
  dd { margin: 0; overflow-wrap: anywhere; }
  .badge { padding: 0 0.4rem; border-radius: 0.25rem; color: var(--tier-ink); font-size: 0.8rem; }
  .blurb { margin: 1rem 0 0; white-space: pre-line; overflow-wrap: anywhere; }
</style>

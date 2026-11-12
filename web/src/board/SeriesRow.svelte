<script lang="ts">
  import type { Book, Tier } from '../contract/tierlist';

  type Props = {
    number: string;
    book: Book | undefined;
    tier: Tier | undefined;
    /** Whether the row offers an eye: an owned book with a cover. */
    eligible: boolean;
    /** Whether this book is the Series Cover now. */
    front: boolean;
    onopen: () => void;
    onfront: () => void;
  };
  let { number, book, tier, eligible, front, onopen, onfront }: Props = $props();
  const label = 'Use this cover for the series';
  const titleId = $props.id();
</script>

<li class="row" class:missing={!book}>
  <span class="number">#{number}</span>
  <button type="button" class="title" id={titleId} onclick={onopen}>{book?.title ?? 'Not in your library'}</button>
  {#if tier}
    <span class="tier" style:background-color={tier.colour}>{tier.label}</span>
  {:else if book}
    <span class="tier unranked">Unranked</span>
  {/if}
  {#if eligible}
    <button type="button" class="eye" aria-label={label} title={label} aria-pressed={front} aria-describedby={titleId} onclick={onfront}>
      <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
        <path class="lid" d="M1.5 12S5.5 5 12 5s10.5 7 10.5 7-4 7-10.5 7S1.5 12 1.5 12z" />
        <circle class="pupil" cx="12" cy="12" r="3" />
      </svg>
    </button>
  {:else}
    <span class="eye-slot" aria-hidden="true"></span>
  {/if}
</li>

<style>
  .row {
    display: flex; align-items: center; gap: 0.75rem; min-height: 2.75rem;
    padding: 0 0.375rem 0 0.625rem; border: 1px solid var(--border); border-radius: 0.375rem;
    background: var(--surface); color: var(--fg);
  }
  .row.missing { color: var(--muted); border-style: dashed; background: transparent; }
  .number { flex: none; min-width: 2.5rem; color: var(--muted); font-size: 0.85rem; }
  .title {
    flex: 1; min-width: 0; align-self: stretch; padding: 0; border: 0; background: none;
    color: inherit; font: inherit; text-align: start; overflow-wrap: anywhere; cursor: pointer;
  }
  .title:hover { text-decoration: underline; }
  .title:focus-visible, .eye:focus-visible { outline: 2px solid var(--fg); outline-offset: 1px; border-radius: 0.25rem; }
  .tier {
    flex: none; padding: 0 0.45rem; border-radius: 0.25rem;
    color: var(--tier-ink); font-size: 0.8rem; font-weight: 600;
  }
  .tier.unranked { color: var(--muted); border: 1px solid var(--border-strong); }
  .eye, .eye-slot { flex: none; width: 2rem; height: 2rem; }
  .eye {
    display: grid; place-items: center; padding: 0; border: 0; border-radius: 0.25rem;
    background: transparent; color: var(--muted); cursor: pointer;
  }
  .eye:hover { color: var(--fg); }
  .lid { fill: none; stroke: currentColor; stroke-width: 1.75; stroke-linejoin: round; }
  .pupil { fill: none; stroke: currentColor; stroke-width: 1.75; }
  .eye[aria-pressed='true'] { color: var(--fg); }
  .eye[aria-pressed='true'] .lid { fill: currentColor; }
  .eye[aria-pressed='true'] .pupil { fill: var(--surface); stroke: var(--surface); }
</style>

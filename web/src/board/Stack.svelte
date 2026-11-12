<script lang="ts">
  import type { Book, Cover, Series } from '../contract/tierlist';
  import { frontOf, readCount, resolve, sheetsBehind, type StackPick } from './stack';

  type Props = {
    name: string;
    series: Series;
    showCaption: boolean;
    showReadCount: boolean;
    showSheets: boolean;
    books: Record<string, Book>;
    covers: Record<string, Cover>;
    onopen: (pick: StackPick) => void;
  };
  let { name, series, showCaption, showReadCount, showSheets, books, covers, onopen }: Props = $props();

  const all = $derived(resolve(series, books, covers));
  const front = $derived(frontOf(all));
  const count = $derived(readCount(all));
  const behind = $derived(Array.from({ length: sheetsBehind(all) }, (_, index) => index + 1));
  const shade = (amount: number) => `color-mix(in srgb, ${series.colour} ${amount}%, #000)`;
</script>

<figure class="stack" class:flat={!showSheets} aria-label={name} data-override={series.override ? 'true' : undefined}>
  {#if showSheets}
    {#each behind as depth (depth)}
      <span class="behind" style:--depth={depth} style:background={shade(depth === 1 ? 70 : 45)}></span>
    {/each}
  {/if}
  <button
    type="button"
    class="front"
    class:unread={front?.book !== undefined && !front.book.read}
    style:background={front?.cover ? undefined : `linear-gradient(160deg, ${series.colour}, ${shade(45)})`}
    aria-label={`${name}, ${count.read} of ${count.total} read`}
    onclick={() => onopen({ stack: name })}
  >
    {#if front?.cover}
      <img class="cover" src={front.cover.src} alt="" />
    {/if}
    {#if showReadCount}
      <span class="count">{count.read}/{count.total}</span>
    {/if}
    {#if showCaption}
      <span class="name">{name}</span>
    {/if}
  </button>
</figure>

<style>
  .stack {
    position: relative; flex: none;
    width: calc(7.75rem * var(--cover-scale, 1)); height: calc(11.25rem * var(--cover-scale, 1));
    margin: 0;
  }
  .stack.flat { width: calc(7rem * var(--cover-scale, 1)); }
  .behind,
  .front {
    position: absolute; left: 0; top: calc(0.75rem * var(--cover-scale, 1));
    width: calc(7rem * var(--cover-scale, 1)); height: calc(10.5rem * var(--cover-scale, 1));
    box-sizing: border-box; border-radius: 0.375rem;
  }
  .behind {
    transform: translate(calc(var(--depth) * 0.375rem), calc(var(--depth) * -0.375rem));
    border: 1px solid rgb(255 255 255 / 15%);
  }
  .front {
    overflow: hidden; padding: 0; border: 0;
    box-shadow: 0 4px 14px rgb(0 0 0 / 35%);
    font: inherit; cursor: pointer;
  }
  .front:focus-visible { outline: 2px solid var(--fg); outline-offset: 3px; }
  .front.unread .cover { filter: grayscale(1); opacity: 0.55; }
  .cover { display: block; width: 100%; height: 100%; object-fit: cover; }
  .count {
    position: absolute; top: 0.375rem; right: 0.375rem; padding: 0 0.45rem;
    border-radius: 999px; background: var(--on-series); color: var(--tier-ink);
    font-size: 0.7rem; font-weight: 700; line-height: 1.6;
  }
  .name {
    position: absolute; right: 0.375rem; bottom: 0.375rem; left: 0.375rem;
    display: -webkit-box; overflow: hidden; padding: 0.375rem 0.5rem;
    border-radius: 0.3rem; background: var(--caption-bg); color: var(--on-series);
    font-size: 0.75rem; font-weight: 600; line-height: 1.3; text-align: start;
    overflow-wrap: anywhere; -webkit-box-orient: vertical; -webkit-line-clamp: 2; line-clamp: 2;
  }
</style>

<script lang="ts">
  import type { Book, Cover } from '../contract/tierlist';

  type Props = {
    name: string;
    number: string;
    book: Book | undefined;
    cover: Cover | undefined;
    background: string;
    layer: number;
    onopen: () => void;
  };

  let { name, number, book, cover, background, layer, onopen }: Props = $props();
</script>

<button
  type="button"
  class="position"
  class:placeholder={book === undefined}
  class:unread={book !== undefined && !book.read}
  data-number={number}
  style:z-index={layer}
  style:background={book === undefined ? background : undefined}
  aria-label={book ? undefined : `${name} #${number}, not in your library`}
  onclick={onopen}
>
  {#if book && cover}
    <img class="cover" src={cover.src} alt={book.title} />
  {:else if book}
    <span class="frame">
      <span class="title">{book.title}</span>
      <span class="mark">no cover</span>
    </span>
  {:else}
    <span class="frame">
      <span class="series-name">{name}</span>
      <span class="number">{number}</span>
    </span>
  {/if}
</button>

<style>
  .position {
    width: 8rem; max-width: 100%; aspect-ratio: 2 / 3; overflow: hidden; border-radius: 0.375rem;
    border: 1px solid var(--border);
    background: color-mix(in srgb, var(--fg) 6%, var(--bg));
    flex: 0 1 auto; min-width: 0; padding: 0; font: inherit; cursor: pointer;
  }
  .position:focus-visible { outline: 2px solid var(--fg); outline-offset: 2px; }
  .position.unread { opacity: 0.4; filter: grayscale(1); }
  .cover { display: block; width: 100%; height: 100%; object-fit: cover; }
  .frame {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 0.25rem; box-sizing: border-box; height: 100%; padding: 0.375rem; text-align: center;
  }
  .title {
    display: -webkit-box; overflow: hidden; color: var(--fg); font-size: 0.75rem; line-height: 1.3;
    -webkit-box-orient: vertical; -webkit-line-clamp: 2; line-clamp: 2;
  }
  .mark { color: var(--muted); font-size: 0.625rem; letter-spacing: 0.06em; text-transform: uppercase; }
  .series-name, .number { color: var(--on-series); text-shadow: 0 1px 2px rgb(0 0 0 / 45%); }
  .series-name { font-size: 0.8rem; font-weight: 600; }
  .number { font-size: 0.7rem; }
</style>

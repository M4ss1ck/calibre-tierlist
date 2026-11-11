<script lang="ts">
  import type { Book, Cover, Series, Tier } from '../contract/tierlist';
  import type { Selection } from './Detail.svelte';

  interface Drawn {
    number: string;
    book: Book | undefined;
    cover: Cover | undefined;
    label: string;
    colour: string;
  }

  type Props = {
    name: string;
    series: Series;
    books: Record<string, Book>;
    covers: Record<string, Cover>;
    tiers: Tier[];
    onopen: (selection: Selection) => void;
  };

  let { name, series, books, covers, tiers, onopen }: Props = $props();

  const shown = $derived<Drawn[]>(
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
  const owned = $derived(shown.filter((position) => position.book !== undefined));
  const gradient = $derived(
    `linear-gradient(160deg, ${series.colour}, color-mix(in srgb, ${series.colour} 45%, #000))`,
  );
</script>

<figure class="stack" aria-label={name} data-override={series.override ? 'true' : undefined}>
  <div class="positions">
    {#each shown as position, index (index)}
      {@const unread = position.book !== undefined && !position.book.read}
      <button
        type="button"
        class="position"
        class:placeholder={position.book === undefined}
        class:unread
        data-number={position.number}
        style:z-index={shown.length - index}
        style:background={position.book === undefined ? gradient : undefined}
        aria-label={position.book ? undefined : `${name} #${position.number}, not in your library`}
        onclick={() =>
          onopen(position.book ? { book: position.book } : { series: name, number: position.number })}
      >
        {#if position.book && position.cover}
          <img class="cover" src={position.cover.src} alt={position.book.title} />
        {:else if position.book}
          <span class="frame">
            <span class="title">{position.book.title}</span>
            <span class="mark">no cover</span>
          </span>
        {:else}
          <span class="frame">
            <span class="series-name">{name}</span>
            <span class="number">{position.number}</span>
          </span>
        {/if}
      </button>
    {/each}
    {#if series.more > 0}
      <span class="more">+{series.more}</span>
    {/if}
    {#if series.override}
      <span
        class="override"
        role="img"
        aria-label="Series Tier Override"
        title="Series Tier set by Override"
      >
        <svg viewBox="0 0 24 24" width="12" height="12" aria-hidden="true" focusable="false">
          <path
            d="M12 21s7-6.1 7-11.5a7 7 0 1 0-14 0C5 14.9 12 21 12 21z"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linejoin="round"
          />
          <circle cx="12" cy="9.5" r="2.5" fill="currentColor" />
        </svg>
      </span>
    {/if}
  </div>
  <div class="badges">
    {#each owned as position, index (index)}
      <span class="tier-badge" style:background-color={position.colour}>{position.label}</span>
    {/each}
  </div>
</figure>

<style>
  .stack { display: flex; flex-direction: column; gap: 0.3rem; margin: 0; }
  .positions { position: relative; display: flex; align-items: flex-start; }
  .position {
    width: 8rem; aspect-ratio: 2 / 3; overflow: hidden; border-radius: 0.375rem;
    border: 1px solid color-mix(in srgb, var(--fg) 18%, var(--bg));
    background: color-mix(in srgb, var(--fg) 6%, var(--bg));
    flex: none; padding: 0; font: inherit; cursor: pointer;
  }
  .position:focus-visible { outline: 2px solid var(--fg); outline-offset: 2px; }
  .position + .position { margin-left: -3.5rem; }
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
  .series-name, .number { color: #fff; text-shadow: 0 1px 2px rgb(0 0 0 / 45%); }
  .series-name { font-size: 0.8rem; font-weight: 600; }
  .number { font-size: 0.7rem; }
  .more {
    position: absolute; right: 0.25rem; bottom: 0.25rem; z-index: 99; padding: 0 0.35rem;
    border: 1px solid var(--bg); border-radius: 999px; color: var(--bg); font-size: 0.7rem;
    background: color-mix(in srgb, var(--fg) 82%, var(--bg)); line-height: 1.5;
  }
  .override {
    position: absolute; top: 0.25rem; right: 0.25rem; z-index: 100; display: flex;
    padding: 0.15rem; border-radius: 999px; color: var(--bg); line-height: 0;
    background: color-mix(in srgb, var(--fg) 82%, var(--bg));
    box-shadow: 0 1px 2px rgb(0 0 0 / 35%);
  }
  .badges { display: flex; flex-wrap: wrap; gap: 0.25rem; }
  .tier-badge {
    padding: 0 0.35rem; border-radius: 0.25rem; color: #1b1b1f; font-size: 0.7rem; line-height: 1.5;
  }
</style>

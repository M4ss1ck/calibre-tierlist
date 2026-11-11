<script lang="ts">
  import type { Cover } from '../contract/tierlist';

  type Props = { title: string; cover?: Cover | undefined; onopen: () => void };
  let { title, cover, onopen }: Props = $props();
</script>

<article class="card" class:placeholder={!cover}>
  <button type="button" class="open" onclick={onopen}>
    {#if cover}
      <img class="cover" src={cover.src} alt="" />
      <span class="title">{title}</span>
    {:else}
      <span class="frame">
        <span class="title">{title}</span>
        <span class="mark">no cover</span>
      </span>
    {/if}
  </button>
</article>

<style>
  .card {
    width: 8rem;
  }

  .open {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    width: 100%;
    padding: 0;
    border: 0;
    border-radius: 0.375rem;
    background: none;
    color: inherit;
    font: inherit;
    text-align: start;
    cursor: pointer;
  }

  .open:focus-visible {
    outline: 2px solid var(--fg);
    outline-offset: 2px;
  }

  .cover,
  .frame {
    display: block;
    width: 100%;
    aspect-ratio: 2 / 3;
    border: 1px solid color-mix(in srgb, var(--fg) 18%, var(--bg));
    border-radius: 0.375rem;
    background: color-mix(in srgb, var(--fg) 6%, var(--bg));
  }

  .cover {
    object-fit: cover;
  }

  .frame {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.25rem;
    padding: 0.375rem;
    text-align: center;
  }

  .title {
    display: -webkit-box;
    overflow: hidden;
    color: var(--fg);
    font-size: 0.8rem;
    line-height: 1.3;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
    line-clamp: 2;
  }

  .placeholder .title {
    font-size: 0.75rem;
  }

  .mark {
    color: var(--muted);
    font-size: 0.625rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }
</style>

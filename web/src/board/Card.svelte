<script lang="ts">
  import type { Cover } from '../contract/tierlist';

  type Props = { title: string; showCaption: boolean; cover?: Cover | undefined; onopen: () => void };
  let { title, showCaption, cover, onopen }: Props = $props();
</script>

<article class="card" class:placeholder={!cover}>
  <button type="button" class="open" onclick={onopen}>
    {#if cover}
      <img class="cover" src={cover.src} alt="" />
    {:else}
      <span class="frame"><span class="mark">no cover</span></span>
    {/if}
    {#if showCaption}
      <span class="title">{title}</span>
    {/if}
  </button>
</article>

<style>
  .card { flex: none; width: calc(7rem * var(--cover-scale, 1)); }
  .open {
    position: relative; display: block; width: 100%; aspect-ratio: 2 / 3; overflow: hidden;
    padding: 0; border: 0; border-radius: 0.375rem;
    background: color-mix(in srgb, var(--fg) 8%, var(--bg));
    box-shadow: 0 4px 14px rgb(0 0 0 / 30%);
    color: inherit; font: inherit; text-align: start; cursor: pointer;
  }
  .open:focus-visible { outline: 2px solid var(--fg); outline-offset: 3px; }
  .cover, .frame { display: block; width: 100%; height: 100%; }
  .cover { object-fit: cover; }
  .frame {
    box-sizing: border-box; padding: 0.75rem 0.5rem;
    border: 1px solid var(--border); border-radius: 0.375rem; text-align: center;
  }
  .mark { color: var(--muted); font-size: 0.625rem; letter-spacing: 0.06em; text-transform: uppercase; }
  .title {
    position: absolute; right: 0.375rem; bottom: 0.375rem; left: 0.375rem;
    display: -webkit-box; overflow: hidden; padding: 0.375rem 0.5rem;
    border-radius: 0.3rem; background: var(--caption-bg); color: var(--on-series);
    font-size: 0.75rem; font-weight: 600; line-height: 1.3;
    overflow-wrap: anywhere; -webkit-box-orient: vertical; -webkit-line-clamp: 2; line-clamp: 2;
  }
</style>

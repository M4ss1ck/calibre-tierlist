<script lang="ts">
  import type { Cover } from '../contract/tierlist';

  let { title, cover }: { title: string; cover?: Cover | undefined } = $props();
</script>

{#if cover}
  <article class="card">
    <img class="cover" src={cover.src} alt="" />
    <span class="title">{title}</span>
  </article>
{:else}
  <article class="card placeholder">
    <div class="frame">
      <span class="title">{title}</span>
      <span class="mark">no cover</span>
    </div>
  </article>
{/if}

<style>
  .card {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    width: 8rem;
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

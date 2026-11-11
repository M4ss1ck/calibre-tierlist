<script lang="ts">
  import type { TierListData } from '../contract/tierlist';
  import { editable } from './editable';

  /** The board's editable title and what it holds; part of the exported sheet. */
  type Props = { data: TierListData; title: string };
  let { data, title = $bindable() }: Props = $props();

  const books = $derived(Object.keys(data.books).length);
  const series = $derived(Object.keys(data.series).length);
  const meta = $derived(
    [`${books} ${books === 1 ? 'book' : 'books'}`, `${series} series`, data.generated.libraryName]
      .filter(Boolean)
      .join(' · '),
  );

  $effect(() => {
    document.title = title;
  });
</script>

<div class="heading">
  <h1 title="Click to rename" use:editable={{ value: title, onchange: (next) => (title = next) }}></h1>
  <p class="meta">{meta}</p>
</div>

<style>
  .heading {
    display: flex;
    flex: 1 1 22rem;
    flex-direction: column;
    gap: 0.25rem;
    min-width: 0;
  }
  h1 {
    align-self: flex-start;
    max-width: 100%;
    box-sizing: border-box;
    margin: 0 0 0 -0.5rem;
    padding: 0.125rem 0.5rem;
    border: 1px dashed transparent;
    border-radius: 0.5rem;
    font-size: 2.25rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    line-height: 1.15;
    overflow-wrap: anywhere;
    cursor: text;
  }
  h1:hover {
    border-color: var(--border-strong);
  }
  h1:focus {
    outline: 2px solid var(--fg);
    outline-offset: 1px;
    border-color: transparent;
  }
  .meta {
    margin: 0;
    color: var(--muted);
  }
  @media (max-width: 480px) {
    h1 {
      font-size: 1.625rem;
    }
  }
</style>

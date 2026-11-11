<script lang="ts">
  import Detail, { type Selection } from './board/Detail.svelte';
  import Lane from './board/Lane.svelte';
  import SeriesPanel from './board/SeriesPanel.svelte';
  import SheetHeader from './board/SheetHeader.svelte';
  import type { StackPick } from './board/stack';
  import UnrankedSwitch from './board/UnrankedSwitch.svelte';
  import type { TierListData } from './contract/tierlist';
  import ExportButton from './export/ExportButton.svelte';
  import PdfButton from './export/PdfButton.svelte';
  import type { Filters } from './filter/filter';
  import FilterBar from './filter/FilterBar.svelte';
  import type { ThemeChoice } from './theme/theme';
  import ThemePicker from './theme/ThemePicker.svelte';

  let { data }: { data: TierListData } = $props();
  let sheet = $state<HTMLElement>();
  let selection = $state<Selection | undefined>();
  let opened = $state<string | undefined>();
  let unranked = $state(true);
  let theme = $state<ThemeChoice>('system');
  let title = $state('Tier List');
  let labels = $state<Record<string, string>>({});
  let filters = $state<Filters>({ query: '', author: null, tag: null, year: null });

  const lanes = $derived(
    data.lanes
      .filter((lane) => unranked || lane.tier !== null)
      .map((lane) => {
        const id = lane.tier ?? 'unranked';
        const tier = data.tiers.find((candidate) => candidate.id === lane.tier);
        return { id, lane, label: labels[id] ?? tier?.label ?? 'Unranked', colour: tier?.colour ?? '#8a8a94' };
      }),
  );
  const compiled = $derived(new Date(data.generated.at).toLocaleDateString(undefined, { dateStyle: 'medium' }));

  function open(picked: Selection | StackPick) {
    if ('stack' in picked) opened = picked.stack;
    else selection = picked;
  }
</script>

<main class="board">
  <div class="sheet" bind:this={sheet}>
    <header>
      <SheetHeader {data} bind:title />
      <div class="controls">
        <div class="group">
          <span class="caption">View</span>
          <div class="row">
            <UnrankedSwitch bind:on={unranked} />
            <ThemePicker bind:choice={theme} />
          </div>
        </div>
        <div class="group">
          <span class="caption">Export</span>
          <div class="row">
            <ExportButton board={sheet} />
            <PdfButton />
          </div>
        </div>
      </div>
    </header>
    <FilterBar books={data.books} bind:filters />
    <div class="lanes">
      {#each lanes as entry (entry.id)}
        <Lane
          lane={entry.lane}
          label={entry.label}
          colour={entry.colour}
          books={data.books}
          covers={data.covers}
          series={data.series}
          {filters}
          onopen={open}
          onrename={(label) => (labels = { ...labels, [entry.id]: label })}
        />
      {/each}
    </div>
    <footer>
      <span>{data.generated.libraryName} · compiled {compiled}</span>
      <span>Calibre Tier List</span>
    </footer>
  </div>
  <SeriesPanel
    name={opened}
    series={opened === undefined ? undefined : data.series[opened]}
    books={data.books}
    covers={data.covers}
    tiers={data.tiers}
    onpick={(picked) => (selection = picked)}
    onclose={() => (opened = undefined)}
  />
  <Detail {selection} tiers={data.tiers} onclose={() => (selection = undefined)} />
</main>

<style>
  :global(body) {
    margin: 0;
    min-height: 100vh;
    background: var(--bg);
    color: var(--fg);
    font-family: var(--font-sans);
    line-height: 1.45;
  }
  .board { max-width: 85rem; margin: 0 auto; }
  .sheet { display: flex; flex-direction: column; gap: 1.5rem; padding: 2.5rem 2rem 3rem; }
  header { display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between; gap: 1.25rem 2rem; }
  .controls { display: flex; flex-wrap: wrap; align-items: flex-end; gap: 1rem 1.5rem; }
  .group { display: flex; flex-direction: column; gap: 0.375rem; }
  .group + .group { padding-left: 1.5rem; border-left: 1px solid var(--border); }
  .row { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem 1rem; }
  .caption {
    color: var(--muted);
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }
  .lanes { overflow: hidden; border: 1px solid var(--border); border-radius: 0.875rem; }
  footer {
    display: flex; flex-wrap: wrap; justify-content: space-between; gap: 0.5rem 1.5rem;
    padding-top: 1rem; border-top: 1px solid var(--border); color: var(--muted); font-size: 0.8rem;
  }
  @media (max-width: 480px) {
    .sheet { padding: 1.25rem 0.75rem 2rem; }
    .group + .group { padding-left: 0; border-left: 0; }
  }
</style>

<script lang="ts">
  import type { PageDefaults } from '../contract/tierlist';
  import Segmented from './Segmented.svelte';
  import Switch from './Switch.svelte';
  import { COVER_SIZE_OPTIONS, GAP_OPTIONS, PAGE_WIDTH_OPTIONS } from './view';

  /** The View Panel: the Page Defaults the reader changes for this session. Nothing here is saved. */
  type Props = { view: PageDefaults; defaults: PageDefaults };
  let { view = $bindable(), defaults }: Props = $props();

  let open = $state(false);
  let trigger = $state<HTMLButtonElement>();

  const emptyOptions: { value: 'shown' | 'hidden'; label: string }[] = [
    { value: 'shown', label: 'Shown' },
    { value: 'hidden', label: 'Hidden' },
  ];

  const emptyShown = $derived(view.emptyLane !== 'hidden');

  function setEmpty(next: 'shown' | 'hidden') {
    const back = defaults.emptyLane === 'hidden' ? 'default' : defaults.emptyLane;
    view.emptyLane = next === 'shown' ? back : 'hidden';
  }

  function close() {
    open = false;
    trigger?.focus();
  }
</script>

<svelte:window
  onkeydown={(event) => {
    if (open && event.key === 'Escape') close();
  }}
/>

<div class="anchor">
  <button
    type="button"
    class="trigger"
    bind:this={trigger}
    aria-expanded={open}
    aria-controls="view-panel"
    onclick={() => (open = !open)}
  >
    <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false">
      <path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0" />
      <circle cx="16" cy="6" r="2" /><circle cx="10" cy="12" r="2" /><circle cx="18" cy="18" r="2" />
    </svg>
    Customize view
  </button>
  {#if open}
    <button type="button" class="catch" tabindex="-1" aria-label="Close" onclick={close}></button>
    <div id="view-panel" class="popover" role="dialog" aria-label="Customize view">
      <fieldset>
        <legend>Lanes</legend>
        <Switch label="Tier labels" bind:on={view.showLabels} />
        <Switch label="Tier descriptions" bind:on={view.showDescriptions} />
        <Switch label="Unranked lane" bind:on={view.showUnranked} />
        <div class="row"><span>Empty message</span>
          <Segmented label="Empty message" options={emptyOptions} value={emptyShown ? 'shown' : 'hidden'} onpick={setEmpty} />
        </div>
        <div class="row"><span>Gap</span>
          <Segmented label="Lane gap" options={GAP_OPTIONS} bind:value={view.laneGap} />
        </div>
      </fieldset>
      <fieldset>
        <legend>Covers</legend>
        <Switch label="Captions" bind:on={view.showCaptions} />
        <Switch label="Read count" bind:on={view.showReadCount} />
        <div class="row"><span>Size</span>
          <Segmented label="Cover size" options={COVER_SIZE_OPTIONS} bind:value={view.coverSize} />
        </div>
        <div class="row"><span>Gap</span>
          <Segmented label="Cover gap" options={GAP_OPTIONS} bind:value={view.coverGap} />
        </div>
      </fieldset>
      <fieldset>
        <legend>Page</legend>
        <div class="row"><span>Width</span>
          <Segmented label="Page width" options={PAGE_WIDTH_OPTIONS} bind:value={view.pageWidth} />
        </div>
        <Switch label="Counts" bind:on={view.showCounts} />
        <Switch label="Library name" bind:on={view.showLibrary} />
      </fieldset>
      <div class="foot">
        <button type="button" class="link" onclick={() => (view = { ...defaults })}>Reset to page defaults</button>
        <span>Not saved</span>
      </div>
    </div>
  {/if}
</div>

<style>
  .anchor { position: relative; }
  .trigger {
    display: flex; align-items: center; gap: 0.5rem; height: 2.75rem; padding: 0 0.875rem;
    border: 1px solid var(--border); border-radius: 0.625rem; background: var(--surface);
    color: var(--fg); font: inherit; font-size: 0.875rem; font-weight: 500; cursor: pointer;
  }
  .trigger svg { fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; }
  .catch { position: fixed; inset: 0; z-index: 20; border: 0; background: transparent; }
  .popover {
    position: absolute; top: calc(100% + 0.5rem); left: 0; z-index: 21;
    display: flex; flex-direction: column; gap: 1rem; width: 21rem; max-width: calc(100vw - 1.5rem);
    box-sizing: border-box; padding: 1rem; border: 1px solid var(--border); border-radius: 0.875rem;
    background: var(--surface); box-shadow: 0 16px 40px rgb(0 0 0 / 22%); color: var(--fg);
  }
  fieldset { display: flex; flex-direction: column; gap: 0.5rem; margin: 0; padding: 0; border: 0; }
  legend {
    margin-bottom: 0.25rem; color: var(--muted); font-size: 0.7rem; font-weight: 600;
    letter-spacing: 0.08em; text-transform: uppercase;
  }
  .row { display: flex; align-items: center; justify-content: space-between; gap: 1rem; font-size: 0.875rem; }
  .foot {
    display: flex; align-items: center; justify-content: space-between; margin-top: 0.25rem;
    padding-top: 0.75rem; border-top: 1px solid var(--border); color: var(--muted); font-size: 0.75rem;
  }
  .link {
    padding: 0; border: 0; background: none; color: var(--accent); font: inherit;
    font-size: 0.8rem; cursor: pointer;
  }
  .link:focus-visible, .trigger:focus-visible { outline: 2px solid var(--fg); outline-offset: 2px; }
</style>

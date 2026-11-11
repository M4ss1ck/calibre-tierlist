<script lang="ts">
  import { exportPng } from './export';

  type Props = { board: HTMLElement | undefined };
  let { board }: Props = $props();
  let busy = $state(false);
  let status = $state('');

  async function run() {
    if (busy) return;
    if (!board) {
      status = 'PNG export failed: the board is not ready';
      return;
    }
    busy = true;
    status = '';
    try {
      status = await exportPng(board);
    } catch (error) {
      status = `PNG export failed: ${error instanceof Error ? error.message : String(error)}`;
    } finally {
      busy = false;
    }
  }
</script>

<div class="export">
  <button type="button" class="toggle" disabled={busy} onclick={run}>
    {busy ? 'Exporting…' : 'Export PNG'}
  </button>
  <p class="status" role="status">{status}</p>
</div>

<style>
  .export {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.25rem;
  }

  .toggle {
    padding: 0.2rem 0.6rem;
    border: 1px solid var(--border-strong);
    border-radius: 999px;
    background: none;
    color: var(--muted);
    font: inherit;
    font-size: 0.85rem;
    cursor: pointer;
  }

  .toggle:disabled {
    cursor: progress;
    opacity: 0.6;
  }

  .toggle:focus-visible {
    outline: 2px solid var(--fg);
    outline-offset: 2px;
  }

  .status {
    margin: 0;
    max-width: 22rem;
    color: var(--muted);
    font-size: 0.8rem;
    text-align: end;
  }

  .status:empty {
    display: none;
  }
</style>

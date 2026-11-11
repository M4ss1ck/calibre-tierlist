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

<button type="button" class="primary" disabled={busy} onclick={run}>
  <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false">
    <path d="M12 3v12M7 10l5 5 5-5M4 21h16" />
  </svg>
  {busy ? 'Exporting…' : 'Download PNG'}
</button>
<p class="status" role="status">{status}</p>

<style>
  .primary {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    height: 2.75rem;
    padding: 0 1rem;
    border: 0;
    border-radius: 0.625rem;
    background: var(--fg);
    color: var(--bg);
    font: inherit;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
  }
  .primary:disabled {
    cursor: progress;
    opacity: 0.6;
  }
  .primary:focus-visible {
    outline: 2px solid var(--fg);
    outline-offset: 2px;
  }
  svg {
    fill: none;
    stroke: currentColor;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
  }
  .status {
    order: 99;
    flex-basis: 100%;
    margin: 0;
    color: var(--muted);
    font-size: 0.8rem;
  }
  .status:empty {
    display: none;
  }
</style>

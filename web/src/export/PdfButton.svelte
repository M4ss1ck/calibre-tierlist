<script lang="ts">
  /** The toolbar's "Print or PDF" control: the browser's print dialog, on the print stylesheet. */
  function save() {
    window.print();
  }
</script>

<button type="button" class="secondary" onclick={save}>
  <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false">
    <path d="M6 9V3h12v6M6 18H4a1 1 0 0 1-1-1v-6a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v6a1 1 0 0 1-1 1h-2" />
    <path d="M6 14h12v7H6z" />
  </svg>
  Print or PDF
</button>

<style>
  .secondary {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    height: 2.75rem;
    padding: 0 1rem;
    border: 1px solid var(--border-strong);
    border-radius: 0.625rem;
    background: transparent;
    color: var(--fg);
    font: inherit;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
  }
  .secondary:focus-visible {
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
</style>

<script lang="ts">
  /** The toolbar's "Save as PDF" control: the browser's print dialog, on the print stylesheet. */
  function save() {
    window.print();
  }
</script>

<button type="button" class="toggle" onclick={save}>Save as PDF</button>

<style>
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

  .toggle:focus-visible {
    outline: 2px solid var(--fg);
    outline-offset: 2px;
  }
</style>

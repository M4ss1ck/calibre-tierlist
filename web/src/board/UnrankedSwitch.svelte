<script lang="ts">
  /** The on/off switch that shows or hides the Unranked Lane. Not persisted. */
  type Props = { on: boolean };
  let { on = $bindable(true) }: Props = $props();
</script>

<div class="field">
  <button
    id="unranked-switch"
    type="button"
    role="switch"
    aria-checked={on}
    onclick={() => (on = !on)}
  >
    <span class="thumb"></span>
  </button>
  <label for="unranked-switch">Unranked lane</label>
</div>

<style>
  .field {
    display: flex;
    align-items: center;
    gap: 0.625rem;
    height: 2.75rem;
  }
  button {
    display: flex;
    flex: none;
    justify-content: flex-start;
    width: 2.875rem;
    height: 1.75rem;
    box-sizing: border-box;
    padding: 3px;
    border: 0;
    border-radius: 999px;
    background: var(--border-strong);
    cursor: pointer;
  }
  button[aria-checked='true'] {
    justify-content: flex-end;
    background: var(--accent);
  }
  button:focus-visible {
    outline: 2px solid var(--fg);
    outline-offset: 2px;
  }
  .thumb {
    width: 1.375rem;
    height: 1.375rem;
    border-radius: 50%;
    background: var(--on-accent);
  }
  label {
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
  }
</style>

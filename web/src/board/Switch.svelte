<script lang="ts">
  /** A labelled on/off switch: the label toggles it too. Not persisted. */
  type Props = { label: string; on?: boolean };
  let { label, on = $bindable(true) }: Props = $props();

  const id = $props.id();
</script>

<div class="field">
  <label id={`${id}-label`} for={id}>{label}</label>
  <button
    {id}
    type="button"
    role="switch"
    aria-labelledby={`${id}-label`}
    aria-checked={on}
    onclick={() => (on = !on)}
  >
    <span class="thumb"></span>
  </button>
</div>

<style>
  .field {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    font-size: 0.875rem;
  }
  label {
    cursor: pointer;
  }
  button {
    display: flex;
    flex: none;
    justify-content: flex-start;
    width: 2.5rem;
    height: 1.5rem;
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
    width: 1.125rem;
    height: 1.125rem;
    border-radius: 50%;
    background: var(--on-accent);
  }
</style>

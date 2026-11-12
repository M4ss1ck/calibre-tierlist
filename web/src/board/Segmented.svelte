<script lang="ts" generics="T extends string">
  /** A compact row of mutually exclusive choices, like the theme picker. */
  type Option<T extends string> = { value: T; label: string };

  type Props = {
    label: string;
    options: Option<T>[];
    value: T;
    onpick?: (value: T) => void;
  };
  let { label, options, value = $bindable(), onpick }: Props = $props();

  function pick(next: T) {
    value = next;
    onpick?.(next);
  }
</script>

<div class="segmented" role="group" aria-label={label}>
  {#each options as option (option.value)}
    <button type="button" aria-pressed={value === option.value} onclick={() => pick(option.value)}>
      {option.label}
    </button>
  {/each}
</div>

<style>
  .segmented {
    display: flex;
    flex: none;
    gap: 2px;
    padding: 2px;
    border: 1px solid var(--border);
    border-radius: 0.5rem;
  }
  button {
    padding: 0.2rem 0.5rem;
    border: 0;
    border-radius: 0.375rem;
    background: transparent;
    color: var(--muted);
    font: inherit;
    font-size: 0.75rem;
    cursor: pointer;
  }
  button[aria-pressed='true'] {
    background: var(--selected);
    color: var(--fg);
  }
  button:focus-visible {
    outline: 2px solid var(--fg);
    outline-offset: 1px;
  }
</style>

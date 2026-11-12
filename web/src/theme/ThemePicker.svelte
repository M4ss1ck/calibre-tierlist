<script lang="ts">
  import { applyTheme, type ThemeChoice } from './theme';

  type Props = { choice: ThemeChoice };
  let { choice = $bindable('system') }: Props = $props();

  const options: { value: ThemeChoice; label: string; icon: string }[] = [
    { value: 'system', label: 'System', icon: 'M3 5h18v11H3zM8 20h8M12 16v4' },
    {
      value: 'light',
      label: 'Light',
      icon: 'M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8zM12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4',
    },
    { value: 'dark', label: 'Dark', icon: 'M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z' },
  ];

  $effect(() => applyTheme(choice));
</script>

<div class="picker" role="group" aria-label="Theme">
  {#each options as option (option.value)}
    <button
      type="button"
      aria-pressed={choice === option.value}
      onclick={() => (choice = option.value)}
    >
      <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false">
        <path d={option.icon} />
      </svg>
      {option.label}
    </button>
  {/each}
</div>

<style>
  .picker {
    display: flex;
    gap: 2px;
    height: 2.75rem;
    box-sizing: border-box;
    padding: 3px;
    border: 1px solid var(--border);
    border-radius: 0.625rem;
  }
  button {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0 0.75rem;
    border: 0;
    border-radius: 0.45rem;
    background: transparent;
    color: var(--muted);
    font: inherit;
    font-size: 0.875rem;
    font-weight: 500;
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
  svg {
    fill: none;
    stroke: currentColor;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
  }
</style>

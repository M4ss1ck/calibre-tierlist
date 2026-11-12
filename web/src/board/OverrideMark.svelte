<script lang="ts">
  // A badge marking a Stack whose Series Tier is an Override.
</script>

<span class="override" role="img" aria-label="Series Tier Override" title="Series Tier set by Override">
  <svg viewBox="0 0 24 24" width="12" height="12" aria-hidden="true" focusable="false">
    <path
      d="M12 21s7-6.1 7-11.5a7 7 0 1 0-14 0C5 14.9 12 21 12 21z"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linejoin="round"
    />
    <circle cx="12" cy="9.5" r="2.5" fill="currentColor" />
  </svg>
</span>

<style>
  .override {
    position: absolute; top: 1.125rem; left: 0.375rem; z-index: 100; display: flex;
    padding: 0.15rem; border-radius: 999px; color: var(--bg); line-height: 0;
    background: color-mix(in srgb, var(--fg) 82%, var(--bg));
    box-shadow: 0 1px 2px rgb(0 0 0 / 35%);
  }
</style>

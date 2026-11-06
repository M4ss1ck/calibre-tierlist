<script lang="ts">
  let { title }: { title: string } = $props();
</script>

<article class="card">{title}</article>

<style>
  .card {
    padding: 0.5rem 0.75rem;
    border: 1px solid color-mix(in srgb, var(--fg) 18%, var(--bg));
    border-radius: 0.375rem;
    background: color-mix(in srgb, var(--fg) 6%, var(--bg));
    color: var(--fg);
    font-size: 0.9rem;
    line-height: 1.3;
    max-width: 14rem;
  }
</style>

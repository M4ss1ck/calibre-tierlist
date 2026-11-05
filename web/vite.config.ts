import { renameSync } from 'node:fs';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { defineConfig, type Plugin } from 'vite';
import { viteSingleFile } from 'vite-plugin-singlefile';

/**
 * The build entry is index.html, but the plugin fills and ships template.html.
 * Rename the emitted file once everything has been inlined.
 */
function templateHtmlOutput(): Plugin {
  const built = new URL('./dist/index.html', import.meta.url);
  const shipped = new URL('./dist/template.html', import.meta.url);

  return {
    name: 'tierlist-template-html',
    apply: 'build',
    enforce: 'post',
    writeBundle() {
      renameSync(built, shipped);
    },
  };
}

export default defineConfig({
  plugins: [svelte(), viteSingleFile(), templateHtmlOutput()],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    reportCompressedSize: false,
  },
});

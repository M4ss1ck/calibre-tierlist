# Tier List developer tasks: check, test, build, install, itest.

calibre_bin_dir := env("CALIBRE_BIN_DIR", "/opt/calibre")
web_checks := env("WEB_CHECKS", "1")
plugin := "plugin"
plugin_zip := "dist/tierlist.zip"

default:
    @just --list

# Lock in step with pyproject (before any `uv run` re-locks it), lint, type check,
# file length, plus the web package when it exists.
check:
    cd {{plugin}} && uv lock --check
    cd {{plugin}} && uv run ruff check .
    cd {{plugin}} && uv run ruff format --check .
    cd {{plugin}} && uv run pyright
    cd {{plugin}} && uv run python tools/check_file_length.py . ../web
    @if [ -f web/package.json ] && [ "{{web_checks}}" = "1" ]; then \
        pnpm -C web check && pnpm -C web lint && \
        pnpm -C web gen:types && git diff --exit-code web/src/contract/tierlist.ts; \
    else \
        echo "skipping web checks"; \
    fi

# Browser tests for the web board (builds the template first).
webtest:
    pnpm -C web test:e2e

# Unit tests.
test:
    cd {{plugin}} && uv run pytest
    @if [ -f web/package.json ]; then \
        pnpm -C web test:unit; \
    else \
        echo "skipping web unit tests"; \
    fi

# Regenerate the translation template for translators.
pot:
    cd {{plugin}} && uv run python tools/make_pot.py

# Build the plugin zip, with template.html when the web package is built.
build:
    @if [ -f web/package.json ]; then pnpm -C web install --frozen-lockfile && pnpm -C web build; fi
    cd {{plugin}} && uv run python tools/build_zip.py

# Install the built zip into the local calibre.
install: build
    {{calibre_bin_dir}}/calibre-customize -a {{plugin_zip}}

# Install into a throwaway config dir and smoke test the real calibre binary.
itest: build
    #!/usr/bin/env bash
    set -euo pipefail
    config=$(mktemp -d)
    trap 'rm -rf "$config"' EXIT
    export CALIBRE_CONFIG_DIRECTORY="$config" QT_QPA_PLATFORM=offscreen
    "{{calibre_bin_dir}}/calibre-customize" -a "{{plugin_zip}}"
    "{{calibre_bin_dir}}/calibre-debug" -e plugin/itest/smoke.py
    "{{calibre_bin_dir}}/calibre-debug" -e plugin/itest/book_tier.py
    "{{calibre_bin_dir}}/calibre-debug" -e plugin/itest/series_override.py
    "{{calibre_bin_dir}}/calibre-debug" -e plugin/itest/read_state.py
    "{{calibre_bin_dir}}/calibre-debug" -e plugin/itest/read_offer.py
    "{{calibre_bin_dir}}/calibre-debug" -e plugin/itest/config_admin.py
    "{{calibre_bin_dir}}/calibre-debug" -e plugin/itest/config_dialog.py
    "{{calibre_bin_dir}}/calibre-debug" -e plugin/itest/config_import.py
    "{{calibre_bin_dir}}/calibre-debug" -e plugin/itest/compile.py
    "{{calibre_bin_dir}}/calibre-debug" -e plugin/itest/covers.py
    "{{calibre_bin_dir}}/calibre-debug" -e plugin/itest/perf.py
    COMPILED_HTML="$PWD/dist/itest/compiled.html" pnpm -C web exec playwright test tests/compiled.spec.ts

# Point git at the versioned hooks.
hooks:
    git config core.hooksPath .githooks

# Everything a commit must pass.
gate: check test

# Tier List developer tasks: check, test, build, install, itest.

calibre_bin_dir := env("CALIBRE_BIN_DIR", "/opt/calibre")
web_checks := env("WEB_CHECKS", "1")
plugin := "plugin"
plugin_zip := "dist/tierlist.zip"

default:
    @just --list

# Lint, type check, file length, plus the web package when it exists.
check:
    cd {{plugin}} && uv run ruff check .
    cd {{plugin}} && uv run ruff format --check .
    cd {{plugin}} && uv run pyright
    cd {{plugin}} && uv run python tools/check_file_length.py . ../web/src
    @if [ -f web/package.json ] && [ "{{web_checks}}" = "1" ]; then \
        pnpm -C web check && pnpm -C web lint; \
    else \
        echo "skipping web checks"; \
    fi

# Unit tests.
test:
    cd {{plugin}} && uv run pytest

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

# Point git at the versioned hooks.
hooks:
    git config core.hooksPath .githooks

# Everything a commit must pass.
gate: check test

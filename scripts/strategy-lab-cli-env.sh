#!/usr/bin/env bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export NUMBA_CACHE_DIR="${NUMBA_CACHE_DIR:-/private/tmp/jesse-numba-cache}"
export PYTEST_DISABLE_PLUGIN_AUTOLOAD="${PYTEST_DISABLE_PLUGIN_AUTOLOAD:-1}"
export PATH="$ROOT_DIR/.venv/bin:$PATH"

mkdir -p "$NUMBA_CACHE_DIR"

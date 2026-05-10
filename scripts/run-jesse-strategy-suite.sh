#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

DEFAULT_TESTS=(
  tests/test_parent_strategy.py
  tests/test_spot_mode.py
  tests/test_metrics.py
  tests/test_backtest.py
  tests/test_helpers.py
  tests/test_research.py
)

cd "$ROOT_DIR"
"$ROOT_DIR/scripts/run-local-pytest.sh" "${DEFAULT_TESTS[@]}" "$@"

#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# shellcheck source=scripts/strategy-lab-cli-env.sh
source "$ROOT_DIR/scripts/strategy-lab-cli-env.sh"

cd "$ROOT_DIR"

"$ROOT_DIR/scripts/run-local-pytest.sh" \
  tests/test_synthetic_range_bars.py \
  tests/test_range_bar_breakout_pullback_scalp.py \
  tests/test_range_bar_bollinger_mean_reversion.py

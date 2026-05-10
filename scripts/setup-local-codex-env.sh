#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_PYTHON="/opt/homebrew/Caskroom/miniconda/base/bin/python"
PYTHON_BIN="${PYTHON_BIN:-$DEFAULT_PYTHON}"
VENV_DIR="$ROOT_DIR/.venv"

if [ ! -x "$PYTHON_BIN" ]; then
  echo "Python interpreter not found at $PYTHON_BIN" >&2
  exit 1
fi

"$PYTHON_BIN" -c 'import sys; assert sys.version_info[:2] == (3, 12), f"Expected Python 3.12, got {sys.version.split()[0]}"'

if [ ! -d "$VENV_DIR" ]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r "$ROOT_DIR/requirements.txt" -e "$ROOT_DIR"

echo
echo "Jesse local environment is ready."
echo "Python: $VENV_DIR/bin/python"
echo "CLI:    $VENV_DIR/bin/jesse"
echo "Tests:  $ROOT_DIR/scripts/run-local-pytest.sh"
echo
echo "Start Codex with:"
echo "  codex -C $ROOT_DIR --profile jesse"

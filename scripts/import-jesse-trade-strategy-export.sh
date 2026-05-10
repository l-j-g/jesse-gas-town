#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${1:-}"
TARGET_DIR="$ROOT_DIR/references/jesse-trade-strategies/source"

if [ -z "$SOURCE_DIR" ]; then
  echo "Usage: $0 /path/to/downloaded/jesse-trade-strategies" >&2
  exit 1
fi

if [ ! -d "$SOURCE_DIR" ]; then
  echo "Source directory not found: $SOURCE_DIR" >&2
  exit 1
fi

mkdir -p "$TARGET_DIR"

find "$SOURCE_DIR" -type f \( -name '*.py' -o -name '*.json' -o -name '*.md' -o -name '*.txt' \) -print0 \
  | while IFS= read -r -d '' file; do
      relative_path="${file#$SOURCE_DIR/}"
      mkdir -p "$TARGET_DIR/$(dirname "$relative_path")"
      cp "$file" "$TARGET_DIR/$relative_path"
    done

echo "Imported Jesse.Trade strategy export into:"
echo "  $TARGET_DIR"
echo
echo "Note: this directory is gitignored by default to avoid accidentally pushing account-only source."

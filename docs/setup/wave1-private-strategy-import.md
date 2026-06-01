# Wave 1 Private Strategy Import

Purpose: make account-downloaded Jesse.Trade Wave 1 originals importable for local-only backtests without committing private source.

## Source Policy

- Private source lives under `references/jesse-trade-strategies/source/`.
- That directory is gitignored.
- Generated importable packages are written under `.runtime/wave1-private-strategies/`.
- `.runtime/` is gitignored.
- Do not commit generated strategy files.

## Prepare Originals

```bash
/Users/lg/src/jesse/.venv/bin/python scripts/prepare-wave1-private-strategies.py --check-imports
```

This prepares these original classes:

- `KAMA_TrendFollowing`
- `SuperScalper`
- `TrendWaveRiderV2`
- `TurtleV2`

The script writes a local manifest:

```text
.runtime/wave1-private-strategies/manifest.json
```

## Refinement Status

The first refinement queue is tracked in the manifest, but refinement classes are not generated yet:

- `KAMA Pullback Reclaim`
- `SuperScalper Time-Stop Scratch`
- `TrendWaveRiderV2 Shallow Pullback Band`
- `Turtle V2 Failed-Break Time Stop`

These remain docs-only until implemented as Jesse-native variants.

## Validation

Current focused gate:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Users/lg/src/jesse/.venv/bin/python -m pytest tests/test_wave1_private_strategy_prepare.py tests/test_baseline_ma_trend.py
```

Expected result from 2026-06-02:

```text
3 passed
```

## Next Step

Use the prepared originals for baseline backtests first. Only then implement one refinement at a time so original-vs-refinement comparisons stay clean.

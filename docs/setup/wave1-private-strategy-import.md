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

## Generated Refinements

The first refinement queue is generated as local-only subclasses under `.runtime/`:

- `KamaPullbackReclaim`: requires KAMA touch-and-reclaim before taking the base continuation signal.
- `SuperScalperTimeStopScratch`: scratches stagnant scalps after a short bar window.
- `TrendWaveRiderV2ShallowPullbackBand`: accepts shallower CCI pullback resets while keeping base trend gates.
- `TurtleV2FailedBreakTimeStop`: cuts breakouts that fail to show follow-through within a few bars.

These variants are importable for local comparison backtests, but they are not yet alpha evidence. They still need route runs and original-vs-refinement logs.

## Validation

Current focused gate:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Users/lg/src/jesse/.venv/bin/python -m pytest tests/test_wave1_private_strategy_prepare.py tests/test_baseline_ma_trend.py
```

Expected result from 2026-06-02 after refinement generation:

```text
4 passed
```

## Next Step

Use the prepared originals and generated refinements for original-vs-refinement baseline backtests. Keep each verdict tied to fees, slippage, trade count, drawdown, and route robustness.

## Original vs Refinement Runner

```bash
/Users/lg/src/jesse/.venv/bin/python scripts/run-wave1-original-refinement-matrix.py --symbols BTC-USDT --start 2024-01-01 --finish 2024-01-08 --leverage 3
```

Notes:

- Each strategy backtest runs in a child process so a fatal private-strategy runtime abort is recorded as an error row.
- The runner adds `4h` and `6h` data routes because several private strategies call higher-timeframe candles.
- The prep script guards private `ta.supertrend(...)` calls against too-short candle arrays because this Jesse checkout can hard-abort there.
- `3x` leverage is only a research route setting for private strategy compatibility; it is not live trading and is not approval for leverage use.

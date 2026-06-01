# Backtest Smoke: Range-Bar Candidates

Date: 2026-06-02
Exchange: `Binance Perpetual Futures`
Timeframe: `1m`
Date range: `2024-01-01` to `2024-02-01`
Fee: `0.0004`
Leverage: `1x cross`
Data source: imported local Jesse DB `1m` candles

Raw CSV: `docs/backtests/2026-06-02-range-bar-candidates-smoke.csv`

## Commands

Correctness:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Users/lg/src/jesse/.venv/bin/python -m pytest tests/test_synthetic_range_bars.py tests/test_range_bar_breakout_pullback_scalp.py tests/test_range_bar_bollinger_mean_reversion.py
```

Backtest smoke:

```bash
/Users/lg/src/jesse/.venv/bin/python scripts/run-range-bar-candidate-matrix.py --start 2024-01-01 --finish 2024-02-01 --csv docs/backtests/2026-06-02-range-bar-candidates-smoke.csv
```

## Results

| Strategy | Symbol | Net % | Profit Factor | Expectancy | Max DD | Win | Trades | L/S | Decision |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| RangeBarBreakoutPullbackScalp | BTC-USDT | -0.2390 | 0.0000 | -0.2464 | -0.2108 | 0.0000 | 97 | 48/49 | reject |
| RangeBarBreakoutPullbackScalp | ETH-USDT | -3.0121 | 0.1691 | -0.2296 | -2.9225 | 0.2691 | 1312 | 685/627 | reject |
| RangeBarBollingerMeanReversion | BTC-USDT | -2.3617 | 0.0000 | -0.1852 | -2.2511 | 0.0000 | 1275 | 626/649 | reject |
| RangeBarBollingerMeanReversion | ETH-USDT | -3.9163 | 0.2260 | -0.2426 | -3.5573 | 0.3662 | 1614 | 805/809 | reject |

## Review

Both executable range-bar candidates pass framework/correctness tests, but fail
this first imported-candle smoke slice after fees. The trade counts are high,
expectancy is negative across both BTC and ETH, and drawdown is too large relative
to the short test window.

Verdict: reject these default hyperparameter routes as-is; revise only if the
range size, trade frequency, and fee/slippage model are redesigned before wider
route sweeps.

## Scope Blocker For `jt-cin.5`

This report covers the two implemented new candidates only. The active project
does not yet contain executable Jesse classes for the Wave 1 original/reference
strategies or their refinement variants:

- Wave 1 originals are present as account-downloaded reference source under
  `references/jesse-trade-strategies/source/`, which is intentionally gitignored
  and should not be committed.
- Refinement variants are documented in
  `docs/strategy-refinement-variants-2026-05-11.md`, but are not implemented as
  importable Jesse strategy classes.

Full original-vs-refinement comparison therefore needs a separate import/adapt
step before the remaining acceptance criteria can be completed.

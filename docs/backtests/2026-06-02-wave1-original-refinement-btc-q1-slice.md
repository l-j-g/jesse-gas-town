# Backtest Slice: Wave 1 Originals vs Refinements BTC Q1

Date: 2026-06-02

Purpose: run a broader BTC-only route slice after the local-only Wave 1 import workflow was stabilized. This is still not alpha evidence and not a paper-trade recommendation.

## Command

```bash
/Users/lg/src/jesse/.venv/bin/python scripts/run-wave1-original-refinement-matrix.py --symbols BTC-USDT --start 2024-01-01 --finish 2024-03-01 --leverage 3 --csv docs/backtests/2026-06-02-wave1-original-refinement-btc-q1-slice.csv --json docs/backtests/2026-06-02-wave1-original-refinement-btc-q1-slice.json
```

Focused tests:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Users/lg/src/jesse/.venv/bin/python -m pytest tests/test_wave1_private_strategy_prepare.py tests/test_wave1_original_refinement_matrix.py tests/test_baseline_ma_trend.py
```

## Config

- Exchange: `Binance Perpetual Futures`
- Symbol: `BTC-USDT`
- Date range: `2024-01-01` to `2024-03-01`
- Fee: `0.0004`
- Leverage: `3x cross`
- Data: imported local Jesse DB `1m` candles
- Data routes: `4h`, `6h`
- Source policy: private Jesse.Trade source and generated local imports remain gitignored

## Metrics

| Strategy | TF | Net % | PF | Exp. | Max DD | Sharpe | Win | Trades | Decision |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `KAMA_TrendFollowing` | 15m | -2.1574 | 0.9254 | -16.5956 | -10.7177 | -0.1326 | 0.6154 | 13 | reject: non-positive expectancy after fees |
| `KamaPullbackReclaim` | 15m | -8.7156 | 0.5379 | -145.2594 | -9.6144 | -2.0758 | 0.5000 | 6 | reject: too few trades |
| `SuperScalper` | 15m | 9.1743 | 1.6765 | 50.9683 | -4.8625 | 2.6482 | 0.6667 | 18 | revise: positive slice, needs route robustness |
| `SuperScalperTimeStopScratch` | 15m | -1.1638 | 0.9182 | -4.1563 | -4.8568 | -0.3352 | 0.3214 | 28 | reject: non-positive expectancy after fees |
| `TrendWaveRiderV2` | 15m | 7.9191 | 1.5983 | 98.9889 | -5.3028 | 1.7151 | 0.6250 | 8 | reject: too few trades |
| `TrendWaveRiderV2ShallowPullbackBand` | 15m | 22.6291 | 2.4282 | 174.0701 | -5.3028 | 3.7970 | 0.6923 | 13 | revise: positive slice, needs route robustness |
| `TurtleV2` | 1h | 26.6750 | 3.1338 | 296.3886 | -12.5012 | 3.1431 | 0.4444 | 9 | reject: too few trades |
| `TurtleV2FailedBreakTimeStop` | 1h | 25.1428 | 3.4095 | 251.4276 | -9.3265 | 3.0719 | 0.3000 | 10 | revise: positive slice, needs route robustness |

Raw CSV: `docs/backtests/2026-06-02-wave1-original-refinement-btc-q1-slice.csv`

Raw JSON: `docs/backtests/2026-06-02-wave1-original-refinement-btc-q1-slice.json`

## Original vs Refinement

- `KAMA Pullback Reclaim` worsened the original: `-6.5581` net percentage-point delta, `-128.6638` expectancy delta, and `7` fewer trades.
- `SuperScalper Time-Stop Scratch` worsened the original: `-10.3381` net percentage-point delta and negative expectancy, despite `10` more trades.
- `TrendWaveRiderV2 Shallow Pullback Band` improved this slice: `+14.7100` net percentage-point delta, `+75.0812` expectancy delta, and `5` more trades.
- `Turtle V2 Failed-Break Time Stop` reduced net return by `-1.5322` percentage points but improved max drawdown by `+3.1747` percentage points; trade count is still only `10`.

## Verdict

- Reject `KAMA Pullback Reclaim` for this route slice.
- Reject `SuperScalper Time-Stop Scratch` for this route slice.
- Revise `TrendWaveRiderV2 Shallow Pullback Band`; it is the strongest refinement on this slice but still needs more routes and cost sensitivity.
- Revise `TurtleV2FailedBreakTimeStop`; possible drawdown improvement, but sample is too small.

## Risks And Failure Modes

- One BTC slice is regime-specific and likely overfit-prone.
- `3x` leverage was used for private-source compatibility; liquidation buffer is not evaluated here.
- Trade counts remain low for TrendWaveRiderV2 and Turtle variants.
- Fees are included, but slippage sensitivity is not included in this slice.
- Positive annualized metrics are unstable because the test window is only two months.
- No multi-market or out-of-sample evidence yet.

## Next Step

Run the same matrix on `ETH-USDT` or a longer BTC out-of-sample slice before any candidate reaches HPO-gate discussion.

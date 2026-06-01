# Backtest Smoke: Wave 1 Originals vs Refinements

Date: 2026-06-02

Purpose: verify the local-only Wave 1 import/backtest workflow. This is not alpha evidence and not a paper-trade recommendation.

## Command

```bash
/Users/lg/src/jesse/.venv/bin/python scripts/run-wave1-original-refinement-matrix.py --symbols BTC-USDT --start 2024-01-01 --finish 2024-01-08 --leverage 3 --csv docs/backtests/2026-06-02-wave1-original-refinement-smoke.csv --json docs/backtests/2026-06-02-wave1-original-refinement-smoke.json
```

Focused tests:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Users/lg/src/jesse/.venv/bin/python -m pytest tests/test_wave1_original_refinement_matrix.py tests/test_wave1_private_strategy_prepare.py tests/test_baseline_ma_trend.py
```

## Config

- Exchange: `Binance Perpetual Futures`
- Symbol: `BTC-USDT`
- Date range: `2024-01-01` to `2024-01-08`
- Fee: `0.0004`
- Leverage: `3x cross`
- Data: imported local Jesse DB `1m` candles
- Data routes: `4h`, `6h` for private strategy higher-timeframe references
- Private source policy: account-downloaded strategy source and generated import packages remain gitignored

## Rows

| Strategy | TF | Status | Net % | PF | Exp. | Max DD | Win | Trades | Decision |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `KAMA_TrendFollowing` | 15m | ok | 0.0000 | n/a | n/a | n/a | 0.0000 | 0 | reject: too few trades |
| `KamaPullbackReclaim` | 15m | ok | 0.0000 | n/a | n/a | n/a | 0.0000 | 0 | reject: too few trades |
| `SuperScalper` | 15m | ok | -4.8625 | 0.0000 | -243.1266 | -4.8625 | 0.0000 | 2 | reject: too few trades |
| `SuperScalperTimeStopScratch` | 15m | ok | -2.9223 | 0.0000 | -97.4094 | -2.9223 | 0.0000 | 3 | reject: too few trades |
| `TrendWaveRiderV2` | 15m | ok | 2.3910 | 1.6045 | 119.5505 | -3.9553 | 0.5000 | 2 | reject: too few trades |
| `TrendWaveRiderV2ShallowPullbackBand` | 15m | ok | 5.2992 | 2.2389 | 176.6388 | -1.2274 | 0.6667 | 3 | reject: too few trades |
| `TurtleV2` | 1h | ok | -2.7234 | 0.0000 | -272.3409 | -2.7234 | 0.0000 | 1 | reject: too few trades |
| `TurtleV2FailedBreakTimeStop` | 1h | ok | -2.7234 | 0.0000 | -272.3409 | -2.7234 | 0.0000 | 1 | reject: too few trades |

Raw CSV: `docs/backtests/2026-06-02-wave1-original-refinement-smoke.csv`

Raw JSON: `docs/backtests/2026-06-02-wave1-original-refinement-smoke.json`

## Original vs Refinement

- `KAMA Pullback Reclaim`: no difference on this slice because both variants had zero trades.
- `SuperScalper Time-Stop Scratch`: improved this tiny slice by `+1.9403` net percentage points and `+145.7172` expectancy, but both variants were losing and trade count moved only from `2` to `3`.
- `TrendWaveRiderV2 Shallow Pullback Band`: improved this tiny slice by `+2.9082` net percentage points and `+57.0883` expectancy, but trade count moved only from `2` to `3`; this is too little evidence to trust.
- `Turtle V2 Failed-Break Time Stop`: no difference on this slice because both variants produced the same single losing trade.

## Risks And Failure Modes

- Sample is intentionally tiny; every non-error row is rejected for too few trades.
- `3x` leverage was required for some private originals to pass margin checks; leverage/liquidation risk is not evaluated here.
- Positive TrendWaveRiderV2 rows are especially overfit-prone because they have only `2` and `3` trades.
- SuperScalper required a local compatibility guard because Jesse `supertrend` can hard-abort on too-short candle arrays.
- Private source is not committed; reproducibility depends on the local account-downloaded source folder.
- This is workflow evidence only: local import, route setup, metric capture, CSV/JSON logging, and error isolation.

## Next Step

Run a broader Wave 1 matrix with at least one full target slice per candidate before making any alpha decision.

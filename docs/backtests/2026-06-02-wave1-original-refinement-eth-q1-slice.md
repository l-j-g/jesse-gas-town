# Backtest Slice: Wave 1 Originals vs Refinements ETH Q1

Date: 2026-06-02

Purpose: add a second-market check after the BTC Q1 slice. This is still not alpha evidence and not a paper-trade recommendation.

## Command

```bash
/Users/lg/src/jesse/.venv/bin/python scripts/run-wave1-original-refinement-matrix.py --symbols ETH-USDT --start 2024-01-01 --finish 2024-03-01 --leverage 3 --csv docs/backtests/2026-06-02-wave1-original-refinement-eth-q1-slice.csv --json docs/backtests/2026-06-02-wave1-original-refinement-eth-q1-slice.json
```

Focused tests:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Users/lg/src/jesse/.venv/bin/python -m pytest tests/test_wave1_private_strategy_prepare.py tests/test_wave1_original_refinement_matrix.py tests/test_baseline_ma_trend.py
```

## Config

- Exchange: `Binance Perpetual Futures`
- Symbol: `ETH-USDT`
- Date range: `2024-01-01` to `2024-03-01`
- Fee: `0.0004`
- Leverage: `3x cross`
- Data: imported local Jesse DB `1m` candles
- Data routes: `4h`, `6h`
- Source policy: private Jesse.Trade source and generated local imports remain gitignored

## Metrics

| Strategy | TF | Net % | PF | Exp. | Max DD | Sharpe | Win | Trades | Decision |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `KAMA_TrendFollowing` | 15m | -2.7293 | 0.8631 | -27.2927 | -8.7804 | -0.3297 | 0.5000 | 10 | reject: non-positive expectancy after fees |
| `KamaPullbackReclaim` | 15m | 1.3427 | 1.1682 | 26.8535 | -8.2663 | 0.4867 | 0.6000 | 5 | reject: too few trades |
| `SuperScalper` | 15m | -4.8178 | 0.6223 | -37.0600 | -6.8847 | -2.2917 | 0.3846 | 13 | reject: non-positive expectancy after fees |
| `SuperScalperTimeStopScratch` | 15m | -6.0428 | 0.3971 | -28.7753 | -6.0428 | -3.6139 | 0.0952 | 21 | reject: non-positive expectancy after fees |
| `TrendWaveRiderV2` | 15m | 0.8697 | 1.0523 | 10.8707 | -15.5853 | 0.3320 | 0.5000 | 8 | reject: too few trades |
| `TrendWaveRiderV2ShallowPullbackBand` | 15m | 4.5258 | 1.2166 | 41.1435 | -11.2755 | 0.8491 | 0.5455 | 11 | revise: positive slice, needs route robustness |
| `TurtleV2` | 1h | -3.0545 | 0.8758 | -21.8179 | -11.9899 | -0.1867 | 0.2143 | 14 | reject: non-positive expectancy after fees |
| `TurtleV2FailedBreakTimeStop` | 1h | 1.1205 | 1.0586 | 7.4700 | -9.1687 | 0.3619 | 0.1333 | 15 | revise: positive slice, needs route robustness |

Raw CSV: `docs/backtests/2026-06-02-wave1-original-refinement-eth-q1-slice.csv`

Raw JSON: `docs/backtests/2026-06-02-wave1-original-refinement-eth-q1-slice.json`

## Original vs Refinement

- `KAMA Pullback Reclaim` improved this slice by `+4.0719` net percentage points and `+54.1462` expectancy, but only made `5` trades.
- `SuperScalper Time-Stop Scratch` improved expectancy by `+8.2847` but worsened net return by `-1.2250` percentage points; both variants stayed negative.
- `TrendWaveRiderV2 Shallow Pullback Band` improved this slice by `+3.6561` net percentage points, `+30.2727` expectancy, and `3` more trades.
- `Turtle V2 Failed-Break Time Stop` improved this slice by `+4.1750` net percentage points, `+29.2880` expectancy, and `+2.8212` max-drawdown percentage points.

## Verdict

- Reject `KAMA Pullback Reclaim` for now because trade count is too low despite positive ETH result.
- Reject `SuperScalper Time-Stop Scratch` because it stays negative on ETH and worsened BTC.
- Revise `TrendWaveRiderV2 Shallow Pullback Band`; it improved both BTC and ETH Q1 slices, but evidence is still too narrow.
- Revise `TurtleV2FailedBreakTimeStop`; ETH improvement plus BTC drawdown improvement is interesting, but win rate and sample quality are weak.

## Risks And Failure Modes

- This is one ETH slice in an early-2024 regime.
- `3x` leverage remains unproven by liquidation-buffer or slippage testing.
- Fee is included, but no explicit slippage sensitivity is included.
- Positive rows have only `11` to `15` trades.
- Low win rates on Turtle variants can hide fragile payoff concentration.
- No out-of-sample evidence yet.

## Next Step

Run a combined cost-sensitivity pass for `TrendWaveRiderV2ShallowPullbackBand` and `TurtleV2FailedBreakTimeStop` before any HPO-gate discussion.

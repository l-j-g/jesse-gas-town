# Wave 1 Original vs Refinement Q1 Cost Sensitivity

Date: 2026-06-02

## Hypothesis

If a candidate is real enough for follow-up, it should survive a higher effective fee setting that approximates fee plus slippage pressure. This is not a final slippage model; it is a cheap fragility check before longer out-of-sample routes.

## Command

```bash
/Users/lg/src/jesse/.venv/bin/python scripts/run-wave1-original-refinement-matrix.py --symbols BTC-USDT,ETH-USDT --start 2024-01-01 --finish 2024-03-01 --leverage 3 --fee 0.001 --csv docs/backtests/2026-06-02-wave1-original-refinement-q1-cost-001.csv --json docs/backtests/2026-06-02-wave1-original-refinement-q1-cost-001.json
```

## Config

- Exchange: Binance Perpetual Futures
- Symbols: `BTC-USDT`, `ETH-USDT`
- Window: `2024-01-01` to `2024-03-01`
- Leverage: `3x` cross
- Effective fee: `0.001`
- Rows: `16`
- Runtime errors: `0`

## Results

| Strategy | Symbol | Net % | Profit factor | Expectancy | Max DD % | Win rate | Trades | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| KAMA_TrendFollowing | BTC-USDT | -6.5885 | 0.7796 | -50.6804 | -11.9878 | 0.6154 | 13 | reject: non-positive expectancy after fees |
| KAMA_TrendFollowing | ETH-USDT | -6.1577 | 0.7115 | -61.5767 | -10.7206 | 0.5000 | 10 | reject: non-positive expectancy after fees |
| KamaPullbackReclaim | BTC-USDT | -10.6313 | 0.4585 | -177.1890 | -10.6313 | 0.5000 | 6 | reject: too few trades |
| KamaPullbackReclaim | ETH-USDT | -0.4634 | 0.9464 | -9.2680 | -9.0837 | 0.6000 | 5 | reject: too few trades |
| SuperScalper | BTC-USDT | 6.8360 | 1.4847 | 37.9779 | -5.0806 | 0.6667 | 18 | revise: positive slice, needs route robustness |
| SuperScalper | ETH-USDT | -6.2769 | 0.5372 | -48.2841 | -7.6313 | 0.3846 | 13 | reject: non-positive expectancy after fees |
| SuperScalperTimeStopScratch | BTC-USDT | -4.4073 | 0.7265 | -15.7404 | -5.5269 | 0.3214 | 28 | reject: non-positive expectancy after fees |
| SuperScalperTimeStopScratch | ETH-USDT | -8.3551 | 0.3070 | -39.7860 | -8.3551 | 0.0952 | 21 | reject: non-positive expectancy after fees |
| TrendWaveRiderV2 | BTC-USDT | 4.8662 | 1.3438 | 60.8273 | -5.6445 | 0.6250 | 8 | reject: too few trades |
| TrendWaveRiderV2 | ETH-USDT | -1.9802 | 0.8891 | -24.7524 | -16.6382 | 0.5000 | 8 | reject: too few trades |
| TrendWaveRiderV2ShallowPullbackBand | BTC-USDT | 17.0312 | 1.9998 | 131.0091 | -5.6445 | 0.6923 | 13 | revise: positive slice, needs route robustness |
| TrendWaveRiderV2ShallowPullbackBand | ETH-USDT | 0.4859 | 1.0217 | 4.4171 | -13.4642 | 0.5455 | 11 | revise: positive slice, needs route robustness |
| TurtleV2 | BTC-USDT | 23.6595 | 2.7350 | 262.8828 | -13.6363 | 0.4444 | 9 | reject: too few trades |
| TurtleV2 | ETH-USDT | -6.5340 | 0.7578 | -46.6715 | -12.5410 | 0.2143 | 14 | reject: non-positive expectancy after fees |
| TurtleV2FailedBreakTimeStop | BTC-USDT | 21.8504 | 2.7905 | 218.5045 | -10.5040 | 0.2000 | 10 | revise: positive slice, needs route robustness |
| TurtleV2FailedBreakTimeStop | ETH-USDT | -2.7682 | 0.8753 | -18.4545 | -10.8936 | 0.1333 | 15 | reject: non-positive expectancy after fees |

## Original vs Refinement Deltas

| Pair | Symbol | Net delta | Expectancy delta | DD delta | Trade delta | Read |
|---|---:|---:|---:|---:|---:|---|
| KAMA_TrendFollowing -> KamaPullbackReclaim | BTC-USDT | -4.0429 | -126.5086 | 1.3565 | -7 | refinement worse and sample smaller |
| KAMA_TrendFollowing -> KamaPullbackReclaim | ETH-USDT | 5.6943 | 52.3086 | 1.6369 | -5 | improvement too thin; only 5 trades |
| SuperScalper -> SuperScalperTimeStopScratch | BTC-USDT | -11.2433 | -53.7183 | -0.4463 | 10 | refinement fails cost pressure |
| SuperScalper -> SuperScalperTimeStopScratch | ETH-USDT | -2.0781 | 8.4981 | -0.7238 | 8 | both variants reject |
| TrendWaveRiderV2 -> TrendWaveRiderV2ShallowPullbackBand | BTC-USDT | 12.1650 | 70.1817 | -0.0000 | 5 | best survivor, still low sample |
| TrendWaveRiderV2 -> TrendWaveRiderV2ShallowPullbackBand | ETH-USDT | 2.4661 | 29.1695 | 3.1740 | 3 | barely positive but robust enough for next slice |
| TurtleV2 -> TurtleV2FailedBreakTimeStop | BTC-USDT | -1.8090 | -44.3783 | 3.1323 | 1 | drawdown improves, return worsens |
| TurtleV2 -> TurtleV2FailedBreakTimeStop | ETH-USDT | 3.7658 | 28.2170 | 1.6474 | 1 | improvement still negative after costs |

## Decision

- `KamaPullbackReclaim`: reject for now. Cost pressure keeps it weak and under-sampled.
- `SuperScalperTimeStopScratch`: reject. It fails the exact cost test it was meant to improve.
- `TrendWaveRiderV2ShallowPullbackBand`: revise. Best remaining refinement; survives BTC strongly and ETH barely under fee `0.001`, but trade counts remain small.
- `TurtleV2FailedBreakTimeStop`: revise only as drawdown-control idea. BTC remains positive, ETH fails after higher costs; do not promote.
- `SuperScalper` original: revise as baseline-only candidate because BTC survives cost pressure, but ETH rejects.

## Risks

- One Q1 regime only; positive rows may be early-2024 trend/regime artifacts.
- Trade counts remain too low for promotion.
- `3x` leverage still not validated against liquidation buffer.
- Effective fee is a crude slippage proxy, not order-book or spread simulation.
- Private-source normalization may alter exact behavior; keep reproducibility notes attached.

## Next Step

Run out-of-sample slices for `TrendWaveRiderV2ShallowPullbackBand`, `TurtleV2FailedBreakTimeStop`, and `SuperScalper` original before any HPO. Suggested next window: `2024-03-01` to `2024-06-01`, BTC/ETH, fee `0.001`, same `3x` route.

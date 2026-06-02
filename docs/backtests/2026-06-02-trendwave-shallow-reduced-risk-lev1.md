# TrendWave Shallow Reduced-Risk Leverage Gate

Date: 2026-06-02

## Hypothesis

`TrendWaveRiderV2ShallowPullbackBand` was the best Wave 1 refinement, but it split hard by market and depended on `3x` leverage. A smaller notional version should reduce drawdown and allow `1x` routing. If ETH still fails, the problem is not only leverage; it is regime/market fragility.

## Implementation

Added generated local-only refinement:

- `TrendWaveRiderV2ShallowReducedRisk`
- Base: `TrendWaveRiderV2`
- Keeps shallow CCI pullback gate: long below `-75`, short above `75`
- Removes private source `qty * 3` multiplier in `go_long()` and `go_short()`
- Does not optimize parameters

Also added runner support:

- `--pair-filter` to run one strategy pair
- `--extra-pair original:refinement:timeframe` to evaluate non-default generated comparisons

## Commands

Q1 cost slice:

```bash
/Users/lg/src/jesse/.venv/bin/python scripts/run-wave1-original-refinement-matrix.py --extra-pair TrendWaveRiderV2ShallowPullbackBand:TrendWaveRiderV2ShallowReducedRisk:15m --pair-filter TrendWaveRiderV2ShallowReducedRisk --symbols BTC-USDT,ETH-USDT --start 2024-01-01 --finish 2024-03-01 --leverage 1 --fee 0.001 --csv docs/backtests/2026-06-02-trendwave-shallow-reduced-risk-q1-cost-001-lev1.csv --json docs/backtests/2026-06-02-trendwave-shallow-reduced-risk-q1-cost-001-lev1.json
```

Out-of-sample slice:

```bash
/Users/lg/src/jesse/.venv/bin/python scripts/run-wave1-original-refinement-matrix.py --extra-pair TrendWaveRiderV2ShallowPullbackBand:TrendWaveRiderV2ShallowReducedRisk:15m --pair-filter TrendWaveRiderV2ShallowReducedRisk --symbols BTC-USDT,ETH-USDT --start 2024-03-01 --finish 2024-06-01 --leverage 1 --fee 0.001 --csv docs/backtests/2026-06-02-trendwave-shallow-reduced-risk-oos-mar-jun-cost-001-lev1.csv --json docs/backtests/2026-06-02-trendwave-shallow-reduced-risk-oos-mar-jun-cost-001-lev1.json
```

## Results

| Window | Strategy | Symbol | Leverage | Net % | Profit factor | Expectancy | Max DD % | Win rate | Trades | Decision |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Q1 | TrendWaveRiderV2ShallowPullbackBand | BTC-USDT | 1x | n/a | n/a | n/a | n/a | n/a | n/a | blocked: insufficient margin |
| Q1 | TrendWaveRiderV2ShallowPullbackBand | ETH-USDT | 1x | n/a | n/a | n/a | n/a | n/a | n/a | blocked: insufficient margin |
| Q1 | TrendWaveRiderV2ShallowReducedRisk | BTC-USDT | 1x | 5.6149 | 2.0401 | 43.1913 | -1.8815 | 0.6923 | 13 | revise: positive slice, needs route robustness |
| Q1 | TrendWaveRiderV2ShallowReducedRisk | ETH-USDT | 1x | 0.4040 | 1.0541 | 3.6729 | -4.5228 | 0.5455 | 11 | revise: positive slice, needs route robustness |
| OOS | TrendWaveRiderV2ShallowPullbackBand | BTC-USDT | 1x | n/a | n/a | n/a | n/a | n/a | n/a | blocked: insufficient margin |
| OOS | TrendWaveRiderV2ShallowPullbackBand | ETH-USDT | 1x | n/a | n/a | n/a | n/a | n/a | n/a | blocked: insufficient margin |
| OOS | TrendWaveRiderV2ShallowReducedRisk | BTC-USDT | 1x | 13.1111 | 1.7471 | 42.2939 | -5.5911 | 0.7419 | 31 | revise: positive slice, needs route robustness |
| OOS | TrendWaveRiderV2ShallowReducedRisk | ETH-USDT | 1x | -7.0497 | 0.7672 | -23.4988 | -8.1275 | 0.6000 | 30 | reject: non-positive expectancy after fees |

## Comparison To Prior 3x Shallow Evidence

Prior `3x` shallow evidence:

- Q1 BTC: net `17.0312%`, max DD `-5.6445%`
- Q1 ETH: net `0.4859%`, max DD `-13.4642%`
- OOS BTC: net `40.5998%`, max DD `-16.5837%`
- OOS ETH: net `-23.1916%`, max DD `-24.1790%`

Reduced-risk `1x` evidence:

- Q1 BTC: net `5.6149%`, max DD `-1.8815%`
- Q1 ETH: net `0.4040%`, max DD `-4.5228%`
- OOS BTC: net `13.1111%`, max DD `-5.5911%`
- OOS ETH: net `-7.0497%`, max DD `-8.1275%`

Read: lower notional reduces drawdown roughly in line with exposure and makes `1x` route valid. It does not fix ETH OOS expectancy.

## Decision

- `TrendWaveRiderV2ShallowReducedRisk`: revise, not HPO.
- Lower leverage/sizing improves route validity and drawdown, but cross-market robustness still fails.
- Next refinement should target regime filtering, not sizing or HPO.

## Risks

- BTC still dominates evidence.
- ETH OOS remains negative after fees.
- Reduced risk keeps same entry/exit logic; it does not address bad regime selection.
- Trade count is acceptable but still not enough for promotion.

## Next Step

Test one simple regime filter for TrendWave before any HPO. Candidate: require higher-timeframe trend agreement or skip ETH when ADX/MA trend conflict persists. Keep parameter count fixed or near-zero.

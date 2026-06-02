# Wave 1 Original vs Refinement OOS Cost Slice

Date: 2026-06-02

## Hypothesis

Candidates that only work in the January-February 2024 slice are likely regime artifacts. Run the next contiguous out-of-sample window with the same higher effective fee before considering HPO.

## Command

```bash
/Users/lg/src/jesse/.venv/bin/python scripts/run-wave1-original-refinement-matrix.py --symbols BTC-USDT,ETH-USDT --start 2024-03-01 --finish 2024-06-01 --leverage 3 --fee 0.001 --csv docs/backtests/2026-06-02-wave1-original-refinement-oos-mar-jun-cost-001.csv --json docs/backtests/2026-06-02-wave1-original-refinement-oos-mar-jun-cost-001.json
```

## Config

- Exchange: Binance Perpetual Futures
- Symbols: `BTC-USDT`, `ETH-USDT`
- Window: `2024-03-01` to `2024-06-01`
- Leverage: `3x` cross
- Effective fee: `0.001`
- Rows: `16`
- Runtime errors: `0`

## Results

| Strategy | Symbol | Net % | Profit factor | Expectancy | Max DD % | Win rate | Trades | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| KAMA_TrendFollowing | BTC-USDT | -18.7641 | 0.6917 | -64.7038 | -26.3402 | 0.5517 | 29 | reject: non-positive expectancy after fees |
| KAMA_TrendFollowing | ETH-USDT | -33.4283 | 0.4226 | -159.1826 | -37.7421 | 0.3810 | 21 | reject: non-positive expectancy after fees |
| KamaPullbackReclaim | BTC-USDT | -11.9459 | 0.6535 | -91.8912 | -23.2653 | 0.5385 | 13 | reject: non-positive expectancy after fees |
| KamaPullbackReclaim | ETH-USDT | 18.2118 | 2.0695 | 182.1185 | -15.2944 | 0.7000 | 10 | revise: positive slice, needs route robustness |
| SuperScalper | BTC-USDT | -14.2839 | 0.5929 | -44.6371 | -17.0012 | 0.4062 | 32 | reject: non-positive expectancy after fees |
| SuperScalper | ETH-USDT | 3.4759 | 1.1057 | 11.5864 | -8.9724 | 0.4667 | 30 | revise: positive slice, needs route robustness |
| SuperScalperTimeStopScratch | BTC-USDT | -13.6826 | 0.5181 | -24.0046 | -14.5661 | 0.1754 | 57 | reject: non-positive expectancy after fees |
| SuperScalperTimeStopScratch | ETH-USDT | -7.3507 | 0.7459 | -15.3139 | -13.2104 | 0.1875 | 48 | reject: non-positive expectancy after fees |
| TrendWaveRiderV2 | BTC-USDT | 33.3390 | 2.2512 | 185.2165 | -11.3208 | 0.7778 | 18 | revise: positive slice, needs route robustness |
| TrendWaveRiderV2 | ETH-USDT | -26.6045 | 0.5955 | -115.6719 | -30.4362 | 0.6087 | 23 | reject: non-positive expectancy after fees |
| TrendWaveRiderV2ShallowPullbackBand | BTC-USDT | 40.5998 | 1.7308 | 130.9671 | -16.5837 | 0.7419 | 31 | revise: positive slice, needs route robustness |
| TrendWaveRiderV2ShallowPullbackBand | ETH-USDT | -23.1916 | 0.7261 | -77.3055 | -24.1790 | 0.6000 | 30 | reject: non-positive expectancy after fees |
| TurtleV2 | BTC-USDT | -19.1983 | 0.4322 | -101.0438 | -22.0122 | 0.3684 | 19 | reject: non-positive expectancy after fees |
| TurtleV2 | ETH-USDT | -8.5796 | 0.7783 | -53.6228 | -24.8143 | 0.3750 | 16 | reject: non-positive expectancy after fees |
| TurtleV2FailedBreakTimeStop | BTC-USDT | -11.3788 | 0.5778 | -59.8885 | -15.7019 | 0.3684 | 19 | reject: non-positive expectancy after fees |
| TurtleV2FailedBreakTimeStop | ETH-USDT | -4.4612 | 0.8745 | -27.8824 | -22.0097 | 0.3125 | 16 | reject: non-positive expectancy after fees |

## Read

- `TrendWaveRiderV2ShallowPullbackBand` is not cross-market robust yet. BTC out-of-sample is strong, but ETH remains negative with large drawdown.
- `TrendWaveRiderV2` original beats the shallow refinement on BTC expectancy in this OOS slice, while both fail ETH.
- `TurtleV2FailedBreakTimeStop` improves drawdown versus original on both BTC and ETH, but both symbols stay negative after costs.
- `SuperScalper` original flips: BTC fails, ETH is mildly positive. The time-stop refinement fails both.
- `KamaPullbackReclaim` has one strong ETH OOS row but fails BTC and was weak in prior Q1 cost evidence.

## Decision

- No HPO candidate yet.
- Keep `TrendWaveRiderV2ShallowPullbackBand` as a revise candidate only; it needs multi-window robustness and possibly an ETH regime filter.
- Keep `TrendWaveRiderV2` original as comparison baseline, not promoted.
- Reject `SuperScalperTimeStopScratch`.
- Reject `KamaPullbackReclaim` for now despite ETH OOS spike; evidence is inconsistent.
- Reject `TurtleV2FailedBreakTimeStop` as alpha candidate; retain idea only for drawdown-control design.

## Risks

- BTC-positive rows may be trend-regime concentration.
- ETH failures show market-specific fragility.
- `3x` leverage worsens drawdown; liquidation buffer still untested.
- Higher fee proxy still not true spread/slippage modeling.

## Next Step

Create a smaller follow-up task for `TrendWaveRiderV2` and `TrendWaveRiderV2ShallowPullbackBand`: test an ETH/BTC regime filter or lower leverage route, but do not optimize parameters yet.

# Wave 1 Cross-Market Review

Date: 2026-06-02

Scope: BTC-USDT and ETH-USDT, `2024-01-01` to `2024-03-01`, `3x`, fee `0.0004`.

Evidence:

- `docs/backtests/2026-06-02-wave1-original-refinement-btc-q1-slice.md`
- `docs/backtests/2026-06-02-wave1-original-refinement-eth-q1-slice.md`

## Candidate Ranking

1. `TrendWaveRiderV2ShallowPullbackBand`: best refinement so far. It improved both BTC and ETH Q1 slices versus original. Still only `13` BTC trades and `11` ETH trades.
2. `TurtleV2FailedBreakTimeStop`: useful drawdown/expectancy improvement on ETH and drawdown improvement on BTC, but weak win rates and small samples.
3. `SuperScalper`: BTC original was positive, but the time-stop refinement worsened BTC and both SuperScalper variants were negative on ETH.
4. `KAMA_TrendFollowing`: original and refinement are inconsistent across BTC/ETH; pullback reclaim reduced trades too much.

## Decisions

- `KamaPullbackReclaim`: reject for now.
- `SuperScalperTimeStopScratch`: reject for now.
- `TrendWaveRiderV2ShallowPullbackBand`: revise; next test is cost sensitivity and longer/out-of-sample routes.
- `TurtleV2FailedBreakTimeStop`: revise; next test is cost sensitivity and longer/out-of-sample routes.

## Why No Promotion

- Only two markets and one early-2024 window.
- `3x` leverage has not been validated against liquidation risk.
- No slippage sensitivity yet.
- Trade counts are small.
- Positive rows may be regime-specific.
- Private-source compatibility normalization changes runtime behavior enough that every result needs explicit reproducibility notes.

## Next Step

Run a focused cost-sensitivity matrix for:

- `TrendWaveRiderV2` vs `TrendWaveRiderV2ShallowPullbackBand`
- `TurtleV2` vs `TurtleV2FailedBreakTimeStop`

Use BTC-USDT and ETH-USDT over the same Q1 slice with fee/slippage proxy settings before expanding to out-of-sample dates.

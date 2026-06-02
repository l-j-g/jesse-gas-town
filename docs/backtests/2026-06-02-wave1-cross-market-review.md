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

## Cost Sensitivity Follow-Up

Evidence: `docs/backtests/2026-06-02-wave1-original-refinement-q1-cost-001.md`

Command:

```bash
/Users/lg/src/jesse/.venv/bin/python scripts/run-wave1-original-refinement-matrix.py --symbols BTC-USDT,ETH-USDT --start 2024-01-01 --finish 2024-03-01 --leverage 3 --fee 0.001 --csv docs/backtests/2026-06-02-wave1-original-refinement-q1-cost-001.csv --json docs/backtests/2026-06-02-wave1-original-refinement-q1-cost-001.json
```

Result:

- `16` rows, `16` ok, `0` runtime errors.
- `TrendWaveRiderV2ShallowPullbackBand` remains the best refinement; BTC net `17.0312%`, ETH net `0.4859%` at fee `0.001`, still only `13` and `11` trades.
- `TurtleV2FailedBreakTimeStop` remains useful only as a drawdown-control idea; BTC net `21.8504%`, ETH net `-2.7682%`.
- `SuperScalper` original survives BTC cost pressure but rejects ETH; use as baseline-only candidate, not promotion.
- `KamaPullbackReclaim` and `SuperScalperTimeStopScratch` remain rejected.

Updated next step: run out-of-sample `2024-03-01` to `2024-06-01` for `TrendWaveRiderV2ShallowPullbackBand`, `TurtleV2FailedBreakTimeStop`, and `SuperScalper` original at fee `0.001` before any HPO.

## Out-of-Sample Follow-Up

Evidence: `docs/backtests/2026-06-02-wave1-original-refinement-oos-mar-jun-cost-001.md`

Command:

```bash
/Users/lg/src/jesse/.venv/bin/python scripts/run-wave1-original-refinement-matrix.py --symbols BTC-USDT,ETH-USDT --start 2024-03-01 --finish 2024-06-01 --leverage 3 --fee 0.001 --csv docs/backtests/2026-06-02-wave1-original-refinement-oos-mar-jun-cost-001.csv --json docs/backtests/2026-06-02-wave1-original-refinement-oos-mar-jun-cost-001.json
```

Result:

- `16` rows, `16` ok, `0` runtime errors.
- `TrendWaveRiderV2ShallowPullbackBand` is not cross-market robust yet: BTC net `40.5998%`, ETH net `-23.1916%`.
- `TrendWaveRiderV2` original also splits: BTC net `33.3390%`, ETH net `-26.6045%`.
- `SuperScalper` flips from Q1: BTC net `-14.2839%`, ETH net `3.4759%`.
- `TurtleV2FailedBreakTimeStop` improves drawdown versus original but remains negative on both BTC and ETH.
- No HPO candidate yet.

Updated next step: create a smaller follow-up for `TrendWaveRiderV2` and `TrendWaveRiderV2ShallowPullbackBand` to test regime filtering or lower leverage. Do not optimize parameters yet.

## TrendWave Lower-Leverage Follow-Up

Evidence: `docs/backtests/2026-06-02-trendwave-shallow-reduced-risk-lev1.md`

Result:

- Base `TrendWaveRiderV2ShallowPullbackBand` cannot run at `1x`; private source sizing submits about `3x` notional and hits insufficient margin.
- Generated `TrendWaveRiderV2ShallowReducedRisk` removes the notional multiplier and runs at `1x`.
- Q1 fee `0.001`: BTC net `5.6149%`, ETH net `0.4040%`.
- OOS Mar-Jun fee `0.001`: BTC net `13.1111%`, ETH net `-7.0497%`.
- Lower risk improves drawdown and route validity but does not fix ETH OOS fragility.

Updated next step: test one simple TrendWave regime filter. Do not run HPO yet.

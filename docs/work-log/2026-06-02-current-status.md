# Work Log: Current Status

Date: 2026-06-02

## Current State

- Active review workspace: `/Users/lg/gt/jesse_gas_town/crew/lg`
- Branch: `crew/lg`
- Git state before this log: clean and up to date with `origin/crew/lg`
- Jesse MCP project root: `/Users/lg/gt/jesse_gas_town/crew/lg_mcp_project`
- Jesse app: listening on `127.0.0.1:9000`
- Jesse MCP: listening on `:9002`, reachable from Codex
- Baseline strategy: `strategies/BaselineMaTrend/__init__.py`
- Baseline route: `routes.py`, Binance Perpetual Futures `BTC-USDT` `1h`
- Experiment template: `docs/experiments/TEMPLATE.md`
- First experiment log: `docs/experiments/2026-06-01-workflow-baseline.md`
- Backtest summaries: `docs/backtests/`

## Commands Run

```bash
git status --short
git status --branch --short
git log --oneline -8
find strategies tests scripts docs/backtests docs/experiments docs/work-log docs/setup -maxdepth 2 -type f | sort
tmux has-session -t jesse-mcp
lsof -nP -iTCP:9000 -sTCP:LISTEN
lsof -nP -iTCP:9002 -sTCP:LISTEN
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Users/lg/src/jesse/.venv/bin/python -m pytest tests/test_baseline_ma_trend.py
df -h /Users/lg/gt/jesse_gas_town /Users/lg/src/jesse
gt doctor
```

MCP smoke draft created through Codex Jesse MCP:

```text
backtest_id: 739e6417-0c55-4845-99be-6048f95e620c
dashboard_url: http://127.0.0.1:9000/#/backtest/739e6417-0c55-4845-99be-6048f95e620c
```

## Verified Results

- Focused baseline test passed: `tests/test_baseline_ma_trend.py` -> `1 passed in 6.43s`
- Disk space is no longer the active blocker: about `88Gi` available, `90%` used
- `gt doctor` disk-space check passed: `87.7 GB free (90.5% used)`
- `gt doctor` overall still reports `3` failures and `4` warnings, but not disk or Dolt reachability
- Dolt server reachable per `gt doctor`
- Jesse MCP created a draft successfully, proving Codex can reach the local MCP endpoint

## Existing Research Evidence

- `BaselineMaTrend` establishes the first 1h moving-average trend workflow.
- BTC-USDT real imported-candle backtest from `2024-01-01` to `2024-06-01` produced `33` trades and tiny positive net profit, but evidence is weak.
- BTC/ETH route/regime/cost matrix is logged in `docs/backtests/2026-06-02-baseline-ma-trend-matrix.md`.
- Matrix verdict: keep `BaselineMaTrend` as workflow control; reject it as alpha candidate.

## Proposed Repo / Workflow Structure

- `strategies/`: Jesse-native strategy classes.
- `routes.py`: active minimal local Jesse route.
- `scripts/`: import, backtest, matrix, and suite runners.
- `docs/experiments/`: hypothesis-first experiment logs.
- `docs/backtests/`: metric summaries and raw CSV outputs.
- `docs/work-log/`: session status, commands, assumptions, blockers, next steps.
- `docs/setup/`: local environment, MCP, and Gas Town setup notes.
- `codex-skills/`: project-specific Codex/Gas Town strategy-lab skills.
- `.beads/`: Gas Town issue/work tracking source of truth.

## Active Blockers / Risks

- `jt-cin.5` remains in progress and blocked by `jt-84f`: missing importable Wave 1 original/refinement strategy classes.
- `gt doctor` failures need separate operational cleanup: stale Claude settings, missing agent bead, priming issue.
- `gt doctor` warns of one stuck patrol wisp; witness lane should handle it, not strategy code work.
- Existing Jesse source fork under this crew workspace is still older than the separate Jesse 2.2.2 MCP project; avoid mixing assumptions.
- Baseline evidence is not profitability evidence: too few trades, regime dependency, cost sensitivity, open-trade effects, and likely overfitting risk if optimized too soon.

## Next Tasks

1. Decide whether to continue from baseline workflow or prioritize `jt-84f` so `jt-cin.5` can complete.
2. If continuing baseline MA research, add one refinement only: e.g. regime filter or multi-timeframe confirmation, not parameter optimization.
3. Add fee/slippage and out-of-sample discipline before testing dynamic allocation or leverage.
4. Keep Jesse MCP running in tmux session `jesse-mcp` for Codex-assisted backtest drafts and strategy inspection.

## Update: Wave 1 Private Strategy Import

Added safe local-only prep workflow for `jt-84f`:

```bash
/Users/lg/src/jesse/.venv/bin/python scripts/prepare-wave1-private-strategies.py --check-imports
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Users/lg/src/jesse/.venv/bin/python -m pytest tests/test_wave1_private_strategy_prepare.py tests/test_baseline_ma_trend.py
```

Result:

- Private Jesse.Trade page payloads are parsed locally from gitignored `references/jesse-trade-strategies/source/`.
- Generated importable originals are written only to gitignored `.runtime/wave1-private-strategies/`.
- Import check succeeded for `KAMA_TrendFollowing`, `SuperScalper`, `TrendWaveRiderV2`, and `TurtleV2`.
- Focused pytest passed: `3 passed in 3.00s`.
- Refinements remain docs-only and still need Jesse-native implementation before full original-vs-refinement backtests.

Follow-up progress in the same prep workflow:

- Generated local-only refinement subclasses under ignored `.runtime/wave1-private-strategies/`.
- Import check succeeded for `KamaPullbackReclaim`, `SuperScalperTimeStopScratch`, `TrendWaveRiderV2ShallowPullbackBand`, and `TurtleV2FailedBreakTimeStop`.
- Focused pytest passed after refinement generation: `4 passed in 4.36s`.
- `jt-84f` is now prepared for original-vs-refinement backtest runner work, but still needs actual route metrics before closure.

Follow-up backtest smoke:

```bash
/Users/lg/src/jesse/.venv/bin/python scripts/run-wave1-original-refinement-matrix.py --symbols BTC-USDT --start 2024-01-01 --finish 2024-01-08 --leverage 3 --csv docs/backtests/2026-06-02-wave1-original-refinement-smoke.csv --json docs/backtests/2026-06-02-wave1-original-refinement-smoke.json
```

Result:

- Added child-process-isolated runner so a hard-aborting private strategy records an error row instead of killing the full matrix.
- Added `4h` and `6h` data routes for private higher-timeframe references.
- Normalized old `on_close_position(self, order)` hooks to the current Jesse signature during local prep.
- Smoke rows produced for `4` original/refinement pairs.
- `KAMA`, `TrendWaveRiderV2`, and `TurtleV2` pairs ran to rows; every row rejected or blocked.
- `SuperScalper` pair remains blocked by hard abort in the supertrend path.
- Focused pytest passed after runner work: `10 passed in 4.42s`, then `9 passed in 3.94s`, then `10 passed in 4.42s`.

Follow-up compatibility fix:

- Added a local-only normalization guard around private `ta.supertrend(...)` calls so SuperScalper does not hard-abort on too-short candle arrays.
- Reran Wave 1 smoke with the same command.
- Result: `8` rows, `8` ok, `0` errors, `4` original-vs-refinement comparisons.
- Every row still rejects for too few trades. This remains workflow evidence, not alpha evidence.
- Focused pytest passed after guard: `11 passed in 4.90s`.

Broader BTC slice for `jt-cin.5`:

```bash
/Users/lg/src/jesse/.venv/bin/python scripts/run-wave1-original-refinement-matrix.py --symbols BTC-USDT --start 2024-01-01 --finish 2024-03-01 --leverage 3 --csv docs/backtests/2026-06-02-wave1-original-refinement-btc-q1-slice.csv --json docs/backtests/2026-06-02-wave1-original-refinement-btc-q1-slice.json
```

Result:

- Added `docs/backtests/2026-06-02-wave1-original-refinement-btc-q1-slice.md`.
- `8` rows, `8` ok, `0` errors, `4` comparisons.
- `KamaPullbackReclaim` worsened KAMA on this route slice.
- `SuperScalperTimeStopScratch` worsened SuperScalper on this route slice.
- `TrendWaveRiderV2ShallowPullbackBand` improved this slice but only had `13` trades.
- `TurtleV2FailedBreakTimeStop` slightly reduced net return but improved max drawdown; only `10` trades.
- All positive rows remain `revise`, not HPO or paper-trade candidates.
- Focused pytest after broader slice runner fix: `12 passed in 4.82s`.

ETH Q1 slice and cross-market review:

```bash
/Users/lg/src/jesse/.venv/bin/python scripts/run-wave1-original-refinement-matrix.py --symbols ETH-USDT --start 2024-01-01 --finish 2024-03-01 --leverage 3 --csv docs/backtests/2026-06-02-wave1-original-refinement-eth-q1-slice.csv --json docs/backtests/2026-06-02-wave1-original-refinement-eth-q1-slice.json
```

Result:

- Added `docs/backtests/2026-06-02-wave1-original-refinement-eth-q1-slice.md`.
- Added `docs/backtests/2026-06-02-wave1-cross-market-review.md`.
- `8` ETH rows, `8` ok, `0` errors, `4` comparisons.
- `TrendWaveRiderV2ShallowPullbackBand` improved both BTC and ETH Q1 slices but remains `revise`.
- `TurtleV2FailedBreakTimeStop` improved ETH and improved BTC drawdown, but remains `revise`.
- `KamaPullbackReclaim` and `SuperScalperTimeStopScratch` are rejected for now.
- No candidate promoted: two markets, one regime window, low trade counts, `3x` leverage risk, no slippage sensitivity.
- Focused pytest after ETH slice: `12 passed in 4.93s`.

## Questions Needing User Input

- Should next strategy work prioritize `jt-84f` importability blocker or a fresh MA refinement experiment?
- Should upstream Jesse 2.2.2 be merged/rebased into the crew research fork, or should MCP stay isolated in `lg_mcp_project` for now?

## Update: Jesse 2.2.2 Upstream Merge

User decision: merge upstream Jesse `v2.2.2` into the crew research fork and make upstream update checks a regular step.

Commands:

```bash
git fetch upstream --tags
git fetch origin master --unshallow --tags
git merge-base HEAD v2.2.2
git switch -c codex/merge-jesse-2.2.2
git merge --no-commit v2.2.2
/Users/lg/src/jesse/.venv/bin/python -m pip install -r requirements.txt
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Users/lg/src/jesse/.venv/bin/python -m pytest tests/test_wave1_private_strategy_prepare.py tests/test_wave1_original_refinement_matrix.py tests/test_baseline_ma_trend.py
```

Result:

- Repo was shallow; unshallowed before merge to avoid an unsafe unrelated-history merge.
- Merge from upstream tag `v2.2.2` applied cleanly; only overlapping local/upstream changed file was `AGENTS.md`.
- `jesse/version.py` now reports `__version__ = "2.2.2"`.
- Updated local venv to upstream `requirements.txt`; new 2.2.2 deps included `matplotlib`, `mcp`, FastAPI/Starlette updates, and `jesse-rust==1.1.0`.
- Refreshed editable install metadata with `/Users/lg/src/jesse/.venv/bin/python -m pip install -e .`; package now installs as `jesse-2.2.2`.
- Focused strategy workflow tests passed after merge: `12 passed in 6.26s`.
- Focused strategy workflow tests passed after editable refresh: `12 passed in 4.67s`.
- Added regular upstream update-check guidance to `AGENTS.md`: fetch upstream tags, inspect latest tags, confirm clean status, merge newer release tags on a review branch before strategy code changes, then rerun focused tests.

## Update: Wave 1 Cost Sensitivity

Ran Q1 fee/slippage proxy at effective fee `0.001` after the Jesse `2.2.2` merge:

```bash
/Users/lg/src/jesse/.venv/bin/python scripts/run-wave1-original-refinement-matrix.py --symbols BTC-USDT,ETH-USDT --start 2024-01-01 --finish 2024-03-01 --leverage 3 --fee 0.001 --csv docs/backtests/2026-06-02-wave1-original-refinement-q1-cost-001.csv --json docs/backtests/2026-06-02-wave1-original-refinement-q1-cost-001.json
```

Result:

- Added `docs/backtests/2026-06-02-wave1-original-refinement-q1-cost-001.md/csv/json`.
- Updated `docs/backtests/2026-06-02-wave1-cross-market-review.md`.
- `16` rows, `16` ok, `0` runtime errors.
- `TrendWaveRiderV2ShallowPullbackBand` remains the best refinement but still only revise: BTC net `17.0312%`, ETH net `0.4859%`, low trade counts.
- `TurtleV2FailedBreakTimeStop` remains revise only as drawdown-control idea: BTC positive, ETH negative after costs.
- `KamaPullbackReclaim` and `SuperScalperTimeStopScratch` remain rejected.
- Next evidence: out-of-sample `2024-03-01` to `2024-06-01`, BTC/ETH, fee `0.001`, same `3x` route before HPO.

## Update: Wave 1 Out-of-Sample Cost Slice

Ran the next contiguous OOS slice:

```bash
/Users/lg/src/jesse/.venv/bin/python scripts/run-wave1-original-refinement-matrix.py --symbols BTC-USDT,ETH-USDT --start 2024-03-01 --finish 2024-06-01 --leverage 3 --fee 0.001 --csv docs/backtests/2026-06-02-wave1-original-refinement-oos-mar-jun-cost-001.csv --json docs/backtests/2026-06-02-wave1-original-refinement-oos-mar-jun-cost-001.json
```

Result:

- Added `docs/backtests/2026-06-02-wave1-original-refinement-oos-mar-jun-cost-001.md/csv/json`.
- Updated `docs/backtests/2026-06-02-wave1-cross-market-review.md`.
- `16` rows, `16` ok, `0` runtime errors.
- `TrendWaveRiderV2ShallowPullbackBand`: BTC net `40.5998%`, ETH net `-23.1916%`; not cross-market robust.
- `TrendWaveRiderV2` original: BTC net `33.3390%`, ETH net `-26.6045%`; useful comparison baseline only.
- `SuperScalper` original: BTC net `-14.2839%`, ETH net `3.4759%`; inconsistent.
- `TurtleV2FailedBreakTimeStop`: negative on both BTC and ETH after costs; keep only as drawdown-control idea.
- Decision: no HPO candidate yet. Next task should test regime filtering or lower leverage for TrendWave only.

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

## Questions Needing User Input

- Should next strategy work prioritize `jt-84f` importability blocker or a fresh MA refinement experiment?
- Should upstream Jesse 2.2.2 be merged/rebased into the crew research fork, or should MCP stay isolated in `lg_mcp_project` for now?

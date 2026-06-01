# Work Log: Environment Status

Date: 2026-06-01

## Current State

- Gas Town rig is running at `/Users/lg/gt/jesse_gas_town`.
- Jesse/Gas Town research fork exists at `/Users/lg/src/jesse`.
- Crew workspace is clean at `/Users/lg/gt/jesse_gas_town/crew/lg`.
- Long-term epic exists: `jt-cin` / `Algorithmic Strategy Research Mountain`.
- Convoy `hq-cv-0i735` previously reported `3/9` complete; refresh before using as current truth.
- `jt-cin.4` has been merged via `jt-wisp-k5y` and closed.
- Setup/backtest task `jt-cin.11` tracks the new local project-root baseline work.
- `jesse` MCP is configured in Codex but not live because no valid local Jesse project root is running `jesse run`.

## Commands Run

```bash
gt status
gt mq list jesse_gas_town
gt polecat list jesse_gas_town
git -C /Users/lg/src/jesse fetch --all --prune
git -C /Users/lg/src/jesse merge --ff-only gas-town/master
codex mcp add jesse --url http://localhost:9002/mcp
bd create "Establish local Jesse research project root and baseline 1h MA strategy" ...
gt sling jt-cin.11 jesse_gas_town --agent codex-jesse --merge=local ...
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Users/lg/src/jesse/.venv/bin/python -m pytest tests/test_baseline_ma_trend.py
/Users/lg/src/jesse/.venv/bin/python scripts/run-baseline-ma-trend-backtest.py
```

## Results

- `/Users/lg/src/jesse` fast-forwarded to `gas-town/master` at `4688e344`.
- `/Users/lg/src/jesse` remains divergent from upstream `jesse-ai/master`; this should be handled as a deliberate rebase/merge task, not as incidental setup.
- Disk is again at the Gas Town critical guard, around `24G` free / `97.4%` used; new polecat spawn failed.
- No non-iCloud local Jesse bot project with `routes.py` was found under `/Users/lg/src`, so this repo now has a root Jesse project layer.
- Focused baseline smoke test passed: `1 passed in 3.21s`.
- Synthetic baseline backtest ran and produced metrics: `9` trades, `0%` win rate, `-0.0659%` net profit.

## Assumptions

- Gas Town fork is the active research base.
- Research/backtesting should stay local and non-live.
- No exchange credentials should be created or requested during this milestone.

## Blockers

- Disk pressure blocks new Gas Town polecat spawn.
- Jesse synthetic backtest emitted `closedtrade.updated_at` schema debug messages, likely local DB migration drift.
- Start `jesse run` from that project root so `http://localhost:9002/mcp` works.
- Import or locate real BTC-USDT / ETH-USDT 1m candles.
- Decide whether to rebase Gas Town fork onto upstream Jesse `origin/master`.

## Next Steps

1. Free disk space enough for Gas Town worker spawn and candle imports.
2. Fix/confirm local Jesse DB migrations.
3. Start `jesse run` from this project root so MCP becomes reachable.
4. Import real BTC-USDT or ETH-USDT 1m candles.
5. Rerun the unchanged baseline on real candles before changing strategy logic.

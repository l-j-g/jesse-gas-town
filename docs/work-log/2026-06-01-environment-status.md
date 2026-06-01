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
- Jesse DB migrations added missing `closedtrade` and `order` columns; synthetic backtest reran without the prior `closedtrade.updated_at` debug warning.
- Existing real candles found in Jesse DB, including Binance Perpetual Futures `BTC-USDT` from `2022-12-23` to `2024-12-24`.
- Imported an additional small public slice through Jesse: Bybit USDT Perpetual `BTC-USDT` since `2026-05-25`.
- Real DB-backed baseline backtest ran on Binance Perpetual Futures `BTC-USDT`, `2024-01-01` to `2024-06-01`: `33` trades, `42.4%` win rate, `+0.0233%` net profit.
- `jesse run` starts from the project root and serves the Jesse app at `127.0.0.1:9000`; it also starts LSP at `9001`.
- No process listens on `9002`, so the configured `jesse` MCP endpoint remains unavailable in this runtime.

## Assumptions

- Gas Town fork is the active research base.
- Research/backtesting should stay local and non-live.
- No exchange credentials should be created or requested during this milestone.

## Blockers

- Disk pressure blocks new Gas Town polecat spawn.
- Jesse MCP remains unavailable: `localhost:9002/mcp` refused connection while `jesse run` was serving the app on `9000`.
- ETH route matrix still needs a first logged baseline run.
- Decide whether to rebase Gas Town fork onto upstream Jesse `origin/master`.

## Next Steps

1. Free disk space enough for Gas Town worker spawn and candle imports.
2. Investigate whether this Jesse build has a separate MCP enablement step beyond `jesse run`.
3. Run the unchanged baseline over a BTC/ETH regime matrix.
4. Add fee/slippage sensitivity before optimizing any MA parameters.
5. Keep disk cleanup as an operational blocker for Gas Town worker spawning.

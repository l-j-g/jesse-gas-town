# Local Jesse + Gas Town Research Setup

Purpose: one local crypto strategy research workspace for Jesse strategies, Gas Town task tracking, experiment evidence, prompts, references, and backtest summaries.

## Scope

- Crypto research and backtesting only.
- No live trading setup.
- No exchange API keys.
- No real order execution.
- Prefer Jesse built-in strategy, route, backtest, optimization, and metric features.
- Use Gas Town for coordination, work assignment, context preservation, and reviewable task history.

## Current Repos

- Jesse framework / Gas Town research fork: `/Users/lg/src/jesse`
- Gas Town rig: `/Users/lg/gt/jesse_gas_town`
- Human crew workspace: `/Users/lg/gt/jesse_gas_town/crew/lg`
- Refinery workspace: `/Users/lg/gt/jesse_gas_town/refinery/rig`

## Recommended Working Model

Use `/Users/lg/gt/jesse_gas_town/crew/lg` as the review and planning workspace for now because it is a clean Git worktree with:

- Jesse source tree
- Gas Town docs
- private reference input area
- `.beads` work tracking
- local `.venv`

Use polecats for implementation work through Gas Town. Do not manually edit active polecat worktrees unless recovering stuck work.

## Jesse MCP

Codex has a `jesse` MCP server configured at:

```text
http://localhost:9002/mcp
```

Use the clean Jesse 2.2.2 MCP project root:

```bash
cd /Users/lg/gt/jesse_gas_town/crew/lg_mcp_project
source .venv/bin/activate
jesse run
```

The source fork at `/Users/lg/gt/jesse_gas_town/crew/lg` is still Jesse 1.13.11
and does not expose MCP. The working MCP setup is documented in
`docs/setup/jesse-mcp-investigation.md`.

Fallback when MCP is unavailable:

```bash
./scripts/run-local-pytest.sh <targeted tests>
./scripts/run-jesse-strategy-suite.sh
```

## First Milestone

Establish the workflow, not a profitable strategy:

1. Confirm local Jesse project root and route config.
2. Add a simple 1h MA trend baseline.
3. Run one BTC-USDT or ETH-USDT backtest using available local data.
4. Record command, config, metrics, assumptions, and risks.
5. Decide keep/refine/reject without claiming profitability from one run.

## Safety Rules

- Start from a hypothesis, not indicator stacking.
- Call out overfitting and lookahead risk.
- Prefer 1x futures assumptions until leverage risk is explicitly evaluated.
- Treat fees/slippage and data quality as first-class risks.
- Do not add live exchange credentials.

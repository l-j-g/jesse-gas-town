# Prompts

Use this folder for reusable prompts for Gas Town/Codex workers.

Prompt rules:

- State the bead ID and acceptance criteria.
- Tell worker to use `jesse` MCP first when available.
- Require fallback disclosure when MCP is unavailable.
- Require exact commands and metrics in the final report.
- Require one verdict: keep, refine, reject, or blocked.

Baseline worker prompt:

```text
Use $jesse-gas-town-strategy-lab and $jesse-strategy.
Target crypto research/backtesting only.
Use the Codex MCP server named jesse first when available for Jesse inspection, routes, backtests, optimization, and metrics.
If MCP is unavailable, state that and fall back to repo files plus Jesse scripts.
Do not set up live trading, exchange keys, or real order execution.
Record exact commands, config, metrics, assumptions, risks, blockers, and one next refinement.
```

---
name: jesse-gas-town-strategy-lab
description: "Use when orchestrating Jesse trading strategy research with Gas Town: generating new strategy ideas, creating beads/formulas/convoys, dispatching Codex workers, backtesting candidates, reviewing robustness, and deciding whether a strategy can be promoted to paper-trade candidate. This skill keeps Jesse as the backtest/execution engine and Gas Town as the multi-agent workflow layer."
---

# Jesse Gas Town Strategy Lab

Use this skill when the task involves both Gas Town and Jesse strategy development.

## Core Contract

- Jesse is the source of truth for strategy code, tests, backtests, optimization, and trading semantics.
- Gas Town is the orchestration layer for beads, formulas, convoys, worker dispatch, and handoffs.
- Default market is crypto futures.
- Agents may recommend `paper-trade candidate`; they must not deploy or recommend direct live trading.
- Use the `jesse-strategy` skill doctrine for Strategy lifecycle, order semantics, and evaluation guardrails.

## Required Reading

Read only the files needed for the task:

- `docs/gas-town-strategy-lab.md` for the workflow.
- `docs/gas-town-backtesting-desk.md` for backtesting, tournament ranking, and HPO gates.
- `docs/jesse-trade-example-strategy-references.md` when using Jesse.Trade example strategies as references.
- `docs/gas-town-prompts.md` for reusable prompts.
- `docs/jesse-strategy-playbook.md` for Strategy lifecycle and order rules.
- `docs/jesse-strategy-evaluation.md` for metric and robustness gates.

## Workflow

1. Convert broad requests into a bead or formula-backed workflow.
2. For idea work, require edge thesis, archetype, target regime, invalid regime, entry trigger, exit/risk model, and first validation plan.
3. For implementation work, keep changes Jesse-native and add focused tests.
4. For evaluation work, report net profit, profit factor, expectancy, max drawdown, trade count, regime notes, and parameter sensitivity.
5. For Backtesting Desk work, evaluate asset, timeframe, and leverage routes before HPO.
6. Rank candidates before HPO and require an HPO gate before optimization.
7. End every candidate review with one verdict: `reject`, `revise`, `hpo-candidate`, or `paper-trade candidate`.

## Gas Town Defaults

- Rig: `jesse_gas_town`
- Preferred agent: `codex-jesse`
- Merge mode: `local` for research and candidate evaluation.
- Formula prefix: `jt-strategy-*`
- Backtesting Desk formulas: `jt-backtest-*`, `jt-strategy-tournament`, and `jt-hpo-*`
- Jesse.Trade reference formula: `jt-strategy-reference-intake`
- Use `gt sling <bead> jesse_gas_town --agent codex-jesse --merge=local` for worker dispatch.
- Source `scripts/strategy-lab-cli-env.sh` before direct Jesse CLI/backtest/optimization commands.

## Review Rules

- Check framework correctness before alpha quality.
- Treat raw backtest profit as insufficient.
- Reject fragile candidates with too few trades, unstable nearby parameters, excessive drawdown, or profits concentrated in one regime.
- Promote to HPO only when baseline tests/backtests pass, asset/timeframe/leverage route evidence is usable, and the search space is small, thesis-linked, and worth the compute.
- Treat leverage as a candidate property that must be earned by drawdown, stop distance, slippage, and liquidation-buffer evidence.
- Treat account-downloaded Jesse.Trade strategy code as private input unless the user explicitly asks to commit it.
- Do not create live configs or restart Jesse unless explicitly asked.
- Use `jh.debug()` for strategy debug output, never `print()`.

## Output Shape

For strategy reports, include:

- thesis
- target/failure regime
- implementation summary
- tests/backtests run
- metrics
- recommended asset/timeframe/leverage route
- weakest risk
- verdict

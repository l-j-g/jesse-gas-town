# Gas Town Strategy Lab

This workflow uses Gas Town for orchestration and Jesse for trading logic, backtests, optimization, and framework correctness. Gas Town agents may recommend paper-trade candidates, but live deployment remains a manual decision.

## Default Operating Model

- Market: crypto futures unless a bead says otherwise.
- Data: existing imported Jesse candles.
- Agent: Codex using the `jesse` profile and the `jesse-gas-town-strategy-lab` skill.
- Merge mode: `local` for research work until a candidate passes review.
- Output: every candidate ends with `reject`, `revise`, or `paper-trade candidate`.

## Roles

- Idea scout: proposes strategy ideas from an explicit market edge and regime thesis.
- Strategy implementer: turns one selected idea into a Jesse-native strategy with focused tests.
- Backtest evaluator: runs tests/backtests and summarizes metrics.
- Robustness reviewer: checks lifecycle correctness, overfitting risk, regime fit, and parameter sensitivity.
- Paper gatekeeper: decides whether a strategy is worth paper trading.

## Workflow

1. Create an idea bead from a market behavior, symbol, timeframe, or archetype.
2. Sling it to the Jesse rig with `codex-jesse`.
3. Convert one idea into a build bead only after the thesis is clear.
4. Run strategy-specific tests before backtests.
5. Evaluate profit only with guardrails: profit factor, drawdown, trade count, expectancy, and regime robustness.
6. Promote only to paper-trade candidate, never directly to live.

For backtesting, tournament ranking, tuning, and HPO selection, use the separate Backtesting Desk procedure in `docs/gas-town-backtesting-desk.md`.

## Commands

```bash
cd /Users/lg/gt
gt rig list
gt config agent list
```

```bash
cd /Users/lg/gt/jesse_gas_town/crew/lg
./scripts/run-local-pytest.sh tests/test_synthetic_range_bars.py
```

Create an idea task:

```bash
bd create "Generate crypto futures strategy ideas for BTC range-bar scalping" \
  --type task \
  --labels strategy,idea,futures \
  --acceptance "Return 3 ideas with edge thesis, target regime, failure mode, implementation sketch, and first backtest plan."
```

Sling the task:

```bash
gt sling jt-xxxxx jesse_gas_town --agent codex-jesse --merge=local \
  --args "Use $jesse-gas-town-strategy-lab. Keep live deployment out of scope."
```

Track work:

```bash
gt convoy list
gt feed --problems
gt agents
```

## Candidate Report

Every evaluated strategy must report:

- Edge thesis
- Archetype and target market
- Target regime and failure regime
- Strategy files changed
- Tests run
- Backtest data slice
- Net profit
- Profit factor
- Expectancy
- Max drawdown
- Trade count
- Parameter sensitivity notes
- Regime robustness notes
- Verdict: `reject`, `revise`, or `paper-trade candidate`

## Promotion Gate

A candidate may be marked `paper-trade candidate` only when:

- Jesse lifecycle and order semantics are valid.
- Futures/spot assumptions are explicit.
- Trade count is high enough to make the result meaningful.
- Profit factor and expectancy are positive after fees.
- Drawdown is proportionate to net profit and position sizing.
- Similar nearby parameters do not collapse.
- Results are not dominated by one exceptional market period.

Live trading needs a separate manual checklist, paper-trade evidence, and explicit user approval.

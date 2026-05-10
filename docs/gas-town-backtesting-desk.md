# Gas Town Backtesting Desk

Backtesting Desk is the separate Gas Town objective for evaluating Jesse strategies before any optimization or paper-trade recommendation.

Gas Town owns coordination. Jesse owns strategy correctness, backtests, metrics, and optimization. The desk may recommend HPO or paper trading, but it must not recommend direct live deployment.

## Desk Roles

- Intake analyst: turns a strategy or idea into a testable candidate with market, route, data, and risk assumptions.
- Correctness tester: runs Jesse lifecycle/order tests before any profit judgment.
- Backtest runner: executes baseline backtests and records exact commands, data slice, hyperparameters, and metrics.
- Tournament judge: compares candidates by robustness, not raw profit.
- HPO gatekeeper: selects only candidates worth hyperparameter optimization.

## Standard Desk Flow

1. Intake the candidate strategy, market, timeframe, date range, and thesis.
2. Run framework correctness tests first.
3. Run baseline backtest with default hyperparameters.
4. Run nearby-parameter or alternate-regime checks when the first result looks usable.
5. Compare against current candidates.
6. Output exactly one desk status: `reject`, `revise`, `hpo-candidate`, or `paper-trade candidate`.

## Required Environment

Run Jesse commands from the Gas Town crew workspace:

```bash
cd /Users/lg/gt/jesse_gas_town/crew/lg
source scripts/strategy-lab-cli-env.sh
```

`strategy-lab-cli-env.sh` exports `NUMBA_CACHE_DIR=/private/tmp/jesse-numba-cache`, which is required for direct Jesse CLI usage in the Gas Town clone.

## Desk Commands

Smoke-test the desk:

```bash
./scripts/strategy-lab-backtest-smoke.sh
```

Evaluate one candidate:

```bash
bd cook jt-backtest-candidate --dry-run \
  --var strategy_name=RangeBarBreakoutPullbackScalp \
  --var market="Sandbox BTC-USDT futures 1m fixture"
```

Create a tournament:

```bash
bd cook jt-strategy-tournament --dry-run \
  --var strategies="RangeBarBreakoutPullbackScalp, RangeBarBollingerMeanReversion" \
  --var market="Sandbox BTC-USDT futures 1m fixture"
```

Sling a desk task:

```bash
gt sling jt-xxxxx jesse_gas_town --agent codex-jesse --merge=local \
  --args "Use $jesse-gas-town-strategy-lab. Run Backtesting Desk. No live trading."
```

## Minimum Report

Every desk result must include:

- strategy name
- thesis
- market and route
- exact commands run
- hyperparameters tested
- net profit
- profit factor
- expectancy
- max drawdown
- trade count
- weakest failure mode
- decision: `reject`, `revise`, `hpo-candidate`, or `paper-trade candidate`

## HPO Gate

Promote to `hpo-candidate` only when:

- Jesse lifecycle and futures/spot assumptions are valid.
- Baseline tests pass.
- Baseline backtest has enough trades to be meaningful.
- Profit factor and expectancy are positive after fees.
- Drawdown is proportionate to return and sizing.
- Result is not dominated by one exceptional segment.
- Hyperparameters are few, thesis-linked, and worth searching.

Run HPO only after the HPO gate. HPO output must still go through robustness review before paper-trade status.

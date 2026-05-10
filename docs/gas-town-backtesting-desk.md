# Gas Town Backtesting Desk

Backtesting Desk is the separate Gas Town objective for evaluating Jesse strategies before any optimization or paper-trade recommendation.

Gas Town owns coordination. Jesse owns strategy correctness, backtests, metrics, and optimization. The desk may recommend HPO or paper trading, but it must not recommend direct live deployment.

## Desk Roles

- Intake analyst: turns a strategy or idea into a testable candidate with market, route, data, and risk assumptions.
- Correctness tester: runs Jesse lifecycle/order tests before any profit judgment.
- Backtest runner: executes baseline backtests and records exact commands, data slice, hyperparameters, and metrics.
- Route analyst: evaluates which assets, timeframes, and leverage bands are worth trading before HPO.
- Tournament judge: compares candidates by robustness, not raw profit.
- HPO gatekeeper: selects only candidates worth hyperparameter optimization.

## Standard Desk Flow

1. Intake the candidate strategy, asset universe, timeframes, date range, leverage candidates, and thesis.
2. Run framework correctness tests first.
3. Run baseline backtest with default hyperparameters on the primary route.
4. Run route sweeps across approved assets, timeframes, and leverage candidates when the first result looks usable.
5. Run nearby-parameter or alternate-regime checks on the strongest routes.
6. Compare against current candidates.
7. Output exactly one desk status: `reject`, `revise`, `hpo-candidate`, or `paper-trade candidate`.

## Route And Leverage Evaluation

Asset and leverage selection is part of Backtesting Desk, not a later live-trading afterthought.

Every serious candidate must define:

- asset universe: symbols to test, exchange, futures/spot mode, and reason each asset belongs
- timeframe universe: primary timeframe and any alternate execution or filter timeframes
- leverage candidates: conservative grid such as `1x, 2x, 3x, 5x`; do not exceed the strategy's stop distance and drawdown evidence
- position sizing basis: fixed risk per trade, fixed notional, or volatility-adjusted sizing
- liquidity/slippage assumptions: minimum volume/open interest and fee/slippage model
- liquidation guardrail: reject routes where normal stop-loss distance, adverse gap, or max drawdown creates unacceptable liquidation risk

Route selection must report:

- best asset/timeframe/leverage combination
- runner-up routes
- rejected routes and why
- max drawdown at each leverage candidate
- approximate liquidation buffer for futures routes
- leverage recommendation: `no leverage`, `1x`, `2x`, `3x`, `5x`, or `reject leverage`

Do not promote a strategy to HPO until the route sweep identifies at least one route with positive expectancy after fees and drawdown that remains tolerable at the proposed leverage.

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
  --var market="Sandbox BTC-USDT futures 1m fixture" \
  --var asset_universe="BTC-USDT, ETH-USDT" \
  --var leverage_grid="1x, 2x, 3x"
```

Create a tournament:

```bash
bd cook jt-strategy-tournament --dry-run \
  --var strategies="RangeBarBreakoutPullbackScalp, RangeBarBollingerMeanReversion" \
  --var market="Sandbox BTC-USDT futures 1m fixture" \
  --var asset_universe="BTC-USDT, ETH-USDT, SOL-USDT" \
  --var leverage_grid="1x, 2x, 3x"
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
- asset universe tested
- timeframe universe tested
- leverage grid tested
- recommended asset/timeframe/leverage route
- exact commands run
- hyperparameters tested
- net profit
- profit factor
- expectancy
- max drawdown
- trade count
- liquidation/leverage risk
- weakest failure mode
- decision: `reject`, `revise`, `hpo-candidate`, or `paper-trade candidate`

## HPO Gate

Promote to `hpo-candidate` only when:

- Jesse lifecycle and futures/spot assumptions are valid.
- Baseline tests pass.
- Baseline backtest has enough trades to be meaningful.
- Profit factor and expectancy are positive after fees.
- Drawdown is proportionate to return and sizing.
- At least one asset/timeframe/leverage route remains robust after fees, slippage assumptions, and liquidation-buffer review.
- Result is not dominated by one exceptional segment.
- Hyperparameters are few, thesis-linked, and worth searching.

Run HPO only after the HPO gate. HPO output must still go through robustness review before paper-trade status.

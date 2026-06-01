# Experiment: Workflow Baseline

Date: 2026-06-01
Status: draft
Decision: blocked

## Hypothesis

Before judging strategy quality, the local workflow must reliably connect Jesse strategy code, routes/config, backtest execution, metrics capture, and Gas Town work tracking.

## Simplest Testable Version

Create a baseline 1h MA trend strategy and run a local BTC-USDT or ETH-USDT backtest using available data. Record exact config, command, metrics, risks, and next step.

## Config

- Strategy: pending
- Exchange: pending
- Symbol: BTC-USDT or ETH-USDT depending on available data
- Timeframe: 1h
- Date range: pending data inspection
- Fee model: Jesse config default until explicitly reviewed
- Slippage assumption: pending
- Leverage: 1x research default until liquidation risk is evaluated
- Position sizing: pending

## Exact Command

```bash
pending
```

## Metrics

Pending first backtest.

## Results

No backtest run yet. Current work established repo organization and identified missing local Jesse project/MCP runtime as the main setup blocker.

## Risks And Failure Modes

- data quality: not yet inspected
- lookahead risk: strategy not implemented yet
- too few trades: unknown
- fee/slippage sensitivity: not yet tested
- regime dependency: expected major risk for MA trend systems
- drawdown/liquidation risk: leverage disabled by default until evaluated
- overfitting risk: high if parameters are optimized before baseline evidence

## One Refinement

Verify or create a non-live local Jesse project root with `.env`, `routes.py`, and a safe research config.

## Evidence

- Gas Town epic: `jt-cin`
- Convoy: `hq-cv-0i735`
- Active implementation task: `jt-cin.4`

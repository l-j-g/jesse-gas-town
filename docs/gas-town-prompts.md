# Gas Town Jesse Strategy Prompts

Use these prompts as `bd create` descriptions, `gt sling --args`, or pasted instructions for Codex workers.

## New Strategy Ideas

```text
Use $jesse-gas-town-strategy-lab.

Generate 3 Jesse strategy ideas for crypto futures using this market focus: <focus>.

For each idea, provide:
- edge thesis
- archetype
- target regime
- invalid regime
- entry trigger
- exit and risk model
- minimum hyperparameters
- first test/backtest plan
- why this is not just indicator stacking

Do not write code. Rank the ideas by expected robustness, not raw profit fantasy.
```

## Implement Strategy

```text
Use $jesse-gas-town-strategy-lab.

Implement this selected Jesse strategy idea: <idea>.

Requirements:
- use Jesse Strategy lifecycle correctly
- express entries in go_long/go_short with self.buy/self.sell
- use self.take_profit and self.stop_loss for futures exits
- keep route timeframe and data assumptions explicit
- add focused tests for signal behavior and order semantics
- avoid unrelated refactors

Run targeted pytest for the new strategy. Report changed files and remaining validation needed.
```

## Backtest Evaluate

```text
Use $jesse-gas-town-strategy-lab.

Evaluate strategy <strategy_name> on existing imported crypto futures candles.

Report:
- symbol/exchange/timeframe/date range
- tested hyperparameters
- net profit
- profit factor
- expectancy
- max drawdown
- trade count
- win rate
- longest underwater period if available
- notes on fees, slippage, and position sizing
- verdict: reject, revise, or robustness-review

Do not recommend live trading from one backtest.
```

## Robustness Review

```text
Use $jesse-gas-town-strategy-lab.

Review <strategy_name> for robustness and overfitting.

Check:
- Jesse lifecycle correctness
- futures/spot compatibility
- signal thesis clarity
- parameter sensitivity near chosen values
- performance across trend, range, and drawdown regimes
- whether simpler baseline would explain most of the result

Output the weakest issue first, then a final verdict.
```

## Paper-Trade Candidate Gate

```text
Use $jesse-gas-town-strategy-lab.

Decide whether <strategy_name> should become a paper-trade candidate.

Inputs:
- implementation summary
- test output
- backtest metrics
- robustness review

Return exactly one status:
- reject
- revise
- paper-trade candidate

Include the minimum evidence needed for the status. Do not prepare live deployment.
```

# Jesse Strategy Evaluation

Use this checklist when proposing, reviewing, optimizing, or testing a Jesse strategy.

## Profit Optimization Objective
- Optimize for net profit only within explicit robustness constraints.
- Prefer:
  - high expectancy
  - healthy profit factor
  - acceptable max drawdown
  - enough trades to support the thesis
  - stable behavior across multiple market conditions
- Reject candidates that look profitable only because of:
  - too few trades
  - one exceptional period
  - loose stops and rare large losses
  - excessive parameter sensitivity

## Default Crypto Futures Guardrails
- Treat these as default review gates unless the user explicitly chooses a different risk posture.
- Prefer at least 100 trades before trusting optimization output. Below that, treat conclusions as weak.
- Prefer profit factor above 1.2 for a baseline candidate and materially higher for anything complex.
- Reject candidates with max drawdown that is obviously disproportionate to net profit or position logic.
- Reject candidates that materially degrade after small parameter moves around the chosen optimum.
- Reject candidates whose profits come mostly from one directional regime while claiming to be general-purpose.

## Framework Correctness Gates
- Confirm the strategy uses the `Strategy` lifecycle as intended:
  - signal in `should_long()` / `should_short()`
  - order definition in `go_long()` / `go_short()`
  - live modifications in `update_position()` or execution hooks
- Confirm order shapes are valid and quantities do not exceed position constraints.
- Confirm spot/futures behavior explicitly:
  - no spot shorting
  - no spot TP/SL placement inside `go_long()`
- Confirm filters return callables, not called results.
- Confirm strategy logic prefers Jesse-native indicators, helpers, and properties over custom abstractions.

## Alpha and Risk Review
- State the target regime, failure regime, and invalid conditions for the strategy.
- State the edge in one sentence before reviewing metrics.
- Review metrics beyond a single optimization target:
  - net profit
  - profit factor
  - expectancy
  - win rate
  - drawdown
  - underwater period
  - holding periods
  - open PnL behavior where relevant
- Do not accept a strategy only because it optimized well on Sharpe-like objectives. Review drawdown shape, trade distribution, and payoff asymmetry as separate concerns.
- Check whether added complexity beats a simpler baseline from the same archetype.

## Anti-Overfitting Rules
- Keep hyperparameter ranges justified and narrow enough to reflect a real thesis.
- Explain why each hyperparameter exists; avoid decorative knobs.
- Prefer stable behavior across uptrend, downtrend, and multi-route scenarios over a single optimized slice.
- Treat `objective_function` choice as a tradeoff, not proof of robustness.
- If optimization is used, inspect post-optimization behavior manually rather than trusting the best candidate alone.
- Reject parameter sets that collapse after small perturbations.

## Local Validation Commands
- Targeted strategy/framework tests:
  ```bash
  ./scripts/run-local-pytest.sh tests/test_parent_strategy.py
  ```
- Core Jesse strategy baseline:
  ```bash
  ./scripts/run-jesse-strategy-suite.sh
  ```
- Research/backtest integrations:
  - inspect `jesse/research/backtest.py`
  - inspect `jesse/research/monte_carlo/`

## Scenario Matrix
- Use uptrend and downtrend fixture coverage when possible.
- Use spot and futures modes intentionally; do not assume behavior transfers between them.
- Use multi-route or data-route scenarios when the strategy depends on cross-symbol or higher-timeframe coordination.
- Review framework correctness first, strategy alpha quality second.
- When practical, compare the strategy against a simpler baseline to confirm the added complexity is paying for itself.

## Review Template
- Edge thesis:
  - one sentence
- Archetype and market:
  - what class of strategy this is and where it is supposed to work
- Metrics summary:
  - net profit, profit factor, expectancy, drawdown, trade count
- Guardrail verdict:
  - pass or fail, with the weakest metric called out first
- Robustness verdict:
  - what happens across regimes and nearby parameter values
- Final decision:
  - accept, reject, or simplify and retest

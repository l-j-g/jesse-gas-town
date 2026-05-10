# Jesse Strategy Playbook

This is the framework contract for writing strategies the way Jesse expects, plus the minimum strategy doctrine for building profit-seeking systems without drifting into indicator soup or invalid Jesse usage.

Default strategy-design bias for Codex:
- market: crypto futures
- style: balanced mix across trend and mean-reversion families
- objective: profit with guardrails

## Alpha Design Order
- Start with a concrete market hypothesis:
  - trend continuation
  - pullback continuation
  - range mean reversion
  - volatility breakout
  - exhaustion reversal
- Define the target regime and the failure regime before writing entry code.
- Use indicators to measure regime, trigger, and exit conditions. Do not stack indicators without a distinct role for each.
- Prefer a simple structure:
  - one regime filter
  - one entry trigger
  - one exit framework
- Optimize for positive expectancy and asymmetric payoff, not win rate alone.
- Keep hyperparameters tied to the thesis. Decorative knobs are usually overfitting.

## Core Loop
- `before()` runs before strategy logic on each execution cycle.
- `_check()` handles cancellations, position updates, market-order simulation, and new-entry decisions.
- `should_long()` and `should_short()` decide whether a fresh position should be opened.
- `go_long()` and `go_short()` define entry orders only.
- `update_position()` is for modifying entry, stop-loss, or take-profit orders while a position is open.
- `after()` runs after the strategy cycle.
- `before_terminate()` and `terminate()` handle end-of-backtest cleanup.

## Intended Trade Placement
- Express entries through `self.buy` or `self.sell`, not custom broker flows. Jesse formats, validates, and infers order types from these fields.
- Valid order shapes are `(qty, price)` or a list of those tuples for multi-point entries/exits.
- Jesse infers entry type from price relative to current price:
  - near current price: market
  - better price: limit
  - worse price: stop
- Use `self.take_profit` and `self.stop_loss` as Jesse-native exit fields. Jesse validates, normalizes, cancels/replaces modified exits, and converts some invalid TP/SL prices into market exits when needed.

## Spot vs Futures Rules
- Spot strategies cannot short. `should_short()` must not open spot shorts.
- In spot mode, do not set `self.take_profit` or `self.stop_loss` inside `go_long()`. Set exits after the position opens, typically in `on_open_position()` or later position events.
- Futures strategies may define TP/SL in `go_long()` and `go_short()` if the shapes and quantities are valid.

## Hooks and Shared Behavior
- `filters()` must return callables, not invoked results. Use `return [self.filter_name]`, not `self.filter_name()`.
- `hyperparameters()` returns Jesse hyperparameter descriptors; `dna()` can override defaults by encoding HP values.
- Use route-event hooks for multi-route coordination:
  - `on_route_open_position()`
  - `on_route_close_position()`
  - `on_route_increased_position()`
  - `on_route_reduced_position()`
  - `on_route_canceled()`
- Use lifecycle hooks for executed-order reactions:
  - `on_open_position()`
  - `on_close_position()`
  - `on_increased_position()`
  - `on_reduced_position()`
  - `on_cancel()`

## Preferred Jesse-Native Inputs
- Read indicators from `jesse/indicators/__init__.py` before adding custom indicator logic.
- Use `jesse.helpers` and existing sizing/PNL helpers before inventing new utility code.
- Treat `tests/test_parent_strategy.py`, `tests/test_spot_mode.py`, and related strategy tests as the behavioral spec for intended framework use.
- Use `jh.debug()` for debug output. Do not use `print()`.

## Practical Strategy Patterns
- Trend-following:
  - use a trend filter plus pullback or breakout trigger
  - avoid taking reversal-style entries against a strong regime unless the strategy is explicitly built for that
- Mean reversion:
  - require range conditions or exhaustion evidence
  - exit at realistic reversion targets rather than trend-style runners
- Breakout:
  - require compression, structure break, or volume/momentum confirmation
  - protect quickly against failed breakouts
- Volatility-aware exits:
  - consider ATR-style stop distances or structure-based invalidation over arbitrary fixed percentages

## Strategy Proposal Template
- Edge thesis:
  - one sentence describing the market inefficiency or behavior being exploited
- Archetype:
  - trend pullback, breakout, range mean reversion, or exhaustion reversal
- Target regime:
  - when the strategy should trade
- Invalid regime:
  - when the strategy must stand down
- Entry logic:
  - regime filter plus trigger
- Exit logic:
  - stop-loss, take-profit, and trade-management rules
- Hyperparameters:
  - only the few parameters that materially express the thesis
- Failure modes:
  - what market behavior breaks the thesis

## Archetype Selection Guidance
- Use trend pullback when directional persistence exists and retracements are orderly.
- Use breakout when compression and structure boundaries dominate.
- Use range mean reversion when the market is balanced and trend strength is weak.
- Use exhaustion reversal only when extension, location, and reversal confirmation align.
- Start from one archetype. Add hybrids only after the single-archetype version proves robust.

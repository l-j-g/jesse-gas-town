# Trend-Momentum Breakout Investigation - 2026-05-11

Issue: `jt-cin.10`

Status: `revise`

This is research and framework work only. It is not live-trading guidance.

## Edge Thesis

- Long variant: when a liquid crypto perpetual is already above a rising `20/50/200 EMA` stack, a clean break above recent structure with expanding volume, positive `MACD`, and Bollinger-band acceptance has better continuation expectancy than buying arbitrary strength inside the trend.
- Short variant: when a liquid crypto perpetual is already below a falling `20/50/200 EMA` stack, a break below recent support with expanding volume, negative `MACD`, and lower-band acceptance has better continuation expectancy than fading weakness blindly.

## Prototype Delivered

- Strategy: `jesse/strategies/TrendMomentumBreakout`
- Tests: `tests/test_trend_momentum_breakout.py`
- Registry wiring: `jesse/strategies/__init__.py`

The prototype is a Jesse-native futures strategy with:

- `should_long()` and `should_short()` for signal gating
- `go_long()` and `go_short()` for entry definition
- Jesse-native `self.stop_loss` and `self.take_profit`
- two-stage exits: `1R` partial, `2.2R` runner
- post-reduction `20 EMA` trailing stop
- short cooldown after a closed trade to avoid repeated re-entry on the same impulse

## Support/Resistance Construction

The user notes asked for short- and long-horizon support/resistance without turning the strategy into a loose indicator pile.

The prototype uses a strict non-lookahead structure model:

- breakout resistance: highest high of the prior `breakout_lookback` bars
- breakdown support: lowest low of the prior `breakout_lookback` bars
- long stop anchor: `max(recent swing low, broken resistance)`
- short stop anchor: `min(recent swing high, broken support)`

This keeps the trigger and invalidation local to the actual breakout shelf.

What is not in the prototype yet:

- higher-timeframe weekly/monthly structure shelves
- explicit rejection entries from resistance or support retests
- the user `20%` significant-high / significant-low regime module

Those remain valid research items, but they need route-level evidence and careful anti-lookahead implementation.

## Variant Review

### Variant A: Bullish Trend-Momentum Breakout

- Archetype: trend continuation / breakout
- Market: crypto perpetual futures, long side
- Target regime:
  - price above `20 EMA`
  - `20 EMA > 50 EMA > 200 EMA`
  - `RSI > 50`
  - volume above `volume SMA(20)` by a thesis-linked multiplier
  - `MACD > signal > 0`
  - close above rolling resistance and above the upper Bollinger Band
- Failure regime:
  - flat or crossing EMAs
  - low-volume breakouts
  - positive trend but no Bollinger expansion
  - breakout that cannot hold above the prior resistance shelf
- Entry:
  - market entry after the confirmed breakout bar
- Exit:
  - initial stop at structure
  - partial at `1R`
  - runner at `2.2R`
  - trail the remainder with `20 EMA` after first reduction

### Variant B: Bear-Market Short Breakdown / Rejection

- Archetype: bearish continuation / breakdown
- Market: crypto perpetual futures, short side
- Target regime:
  - price below `20 EMA`
  - `20 EMA < 50 EMA < 200 EMA`
  - `RSI < 50`
  - volume above `volume SMA(20)` by a thesis-linked multiplier
  - `MACD < signal < 0`
  - close below rolling support and below the lower Bollinger Band
- Failure regime:
  - bear trend already exhausted into very late extension
  - support breaks with weak volume
  - immediate reclaim back inside the broken shelf
- Entry:
  - market entry after the confirmed breakdown bar
- Exit:
  - initial stop at structure
  - partial at `1R`
  - runner at `2.2R`
  - trail the remainder with `20 EMA` after first reduction

The user also asked for rejection-style short behavior. That remains a valid branch, but it is not yet coded into the first prototype because the cleaner first pass is the structural breakdown branch. Rejection entries should be tested separately against BTC and ETH first rather than mixed into the baseline.

## Long-Only And Index-Style Notes

- For stock or index-style long-only usage, disable short routing and keep the `200 EMA` market-risk filter as a hard stand-down rule.
- For altcoin long routes, test a BTC or ETH `200 EMA` proxy as the category risk-on / risk-off filter before trusting the asset’s own local trend.
- The user `20% rally from significant low / 20% drawdown from significant high` rule should be treated as a separate regime module, not as a reverse-entry shortcut.
- That module is still `research-only` here because defining the significant high/low without lookahead needs an explicit swing engine.

## Risk Model

- Position sizing in the prototype is fixed-notional via `position_size_pct`, not live sizing doctrine.
- Research stance should remain conservative:
  - start with `0.25%` to `0.75%` equity risk per trade in real route evaluation
  - avoid correlated concurrent positions
  - reject leverage where normal stop distance plus adverse gap risk compresses liquidation buffer too far

## Hyperparameters

Prototype hyperparameters:

- `fast_ema=20`
- `slow_ema=50`
- `regime_ema=200`
- `breakout_lookback=20`
- `swing_lookback=10`
- `volume_period=20`
- `volume_multiplier=1.3`
- `bb_dev=2.0`
- `position_size_pct=0.03`
- `tp1_r=1.0`
- `tp2_r=2.2`
- `cooldown_bars=5`

Research knobs preserved from the user notes but not all surfaced yet:

- alternate EMA stack: `10/30/200` for faster bear variants
- Bollinger `1.5` deviation for volatile crypto routes
- explicit rejection entry branch
- `20%` regime filter / exit module

## Route Grid For Backtesting Desk

These are the routes worth testing next. They are recommendations, not completed route results.

- `BTC-USDT`
  - `Daily`: slow long-only regime check; likely lower trade count
  - `4h`: strongest first baseline for the long variant
  - `1h`: valid for more entries, but more false-breakout risk
  - leverage: start `1x`, then `2x`; `3x` only after liquidation-buffer review
- `ETH-USDT`
  - `Daily`: slower confirmation route, likely thinner sample
  - `4h`: primary secondary route
  - `1h`: acceptable after BTC baseline
  - leverage: start `1x`, then `2x`; `3x` conditional
- `SOL-USDT`
  - `Daily`: likely trade-light and more regime-sensitive
  - `4h`: acceptable only after BTC and ETH look coherent
  - `1h`: plausible for breakouts, but noise and wick risk are higher
  - leverage: prefer `1x`; `2x` only with strong stop and drawdown evidence; `3x` should start as skeptical

Short-side route bias:

- start with `BTC-USDT` and `ETH-USDT`
- treat `SOL-USDT` shorts as second-wave only
- treat `1h` and `4h` as the primary short routes

## Exact Tests And Backtests Attempted

### Framework / Strategy Validation

Command run:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /Users/lg/src/jesse/.venv/bin/python -m pytest tests/test_trend_momentum_breakout.py
```

Result:

- `3 passed`

Synthetic fixture coverage:

- bullish breakout fixture: `1` profitable long trade
- bearish breakdown fixture: `1` profitable short trade
- low-volume breakout fixture: `0` trades

### Historical Route Backtests

Not run in this pass.

Reason:

- the worktree-local `./scripts/run-local-pytest.sh` and desk smoke path expect `.venv` inside this clone, but that environment is absent here
- no imported `BTC/ETH/SOL` candle set was validated in this task
- without route data and a verified desk runtime, any route-level PnL, profit factor, expectancy, or drawdown claim would be fake precision

## Metrics

Only synthetic fixture evidence exists in this pass:

- trade count: long fixture `1`, short fixture `1`, low-volume fixture `0`
- directionality: both active fixtures closed in the intended direction
- route-quality metrics such as net profit, profit factor, expectancy, and max drawdown: `not yet measured on real BTC/ETH/SOL route data`

## Weakest Risks

- breakout logic can still overtrade in chop if the route-specific volume threshold is too loose
- the short variant is structurally cleaner than the long-only equity interpretation, so it should not be assumed to transfer directly to portfolio-style rules
- the missing `20%` regime module means the user’s favorite long-hold exit logic is still only conceptual here
- no real route sweep means leverage recommendations remain provisional

## Verdict

`revise`

Reason:

- framework correctness is in place
- the prototype expresses the thesis cleanly without violating Jesse order semantics
- but there is still no real route evidence on `BTC/ETH/SOL` across `daily/4h/1h` and `1x/2x/3x`
- the `20%` regime module and rejection-style short branch remain follow-up research items

## Next Step

Run Backtesting Desk on the prototype with:

- assets: `BTC-USDT`, `ETH-USDT`, `SOL-USDT`
- timeframes: `1h`, `4h`, `daily`
- leverage grid: `1x`, `2x`, `3x`
- status gate: do not promote past `revise` until at least one route shows positive expectancy after fees with acceptable drawdown and liquidation buffer

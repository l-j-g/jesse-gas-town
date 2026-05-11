# Trend-Momentum Breakout User Notes - 2026-05-11

Source: user-provided strategy notes for Jesse/Gas Town strategy research.

Purpose: preserve the reference material for later Jesse strategy design, backtesting, refinement, route selection, leverage review, and HPO gating. This is research input only. It is not a live-trading instruction.

## Strategy Name

Trend-Momentum Breakout System

## Core Thesis

Use trend, momentum, volume, volatility, and support/resistance alignment to identify high-probability continuation or breakdown trades.

The system is built around:

- Moving averages for trend and regime.
- RSI for momentum state and divergence.
- Volume for conviction.
- MACD for trend/momentum confirmation.
- Bollinger Bands for volatility context and breakout/rejection behavior.
- Short-term and long-term support/resistance for precise entries, exits, stops, and targets.

## Default Indicator Settings

- Fast EMA: 20 period.
- Slow EMA: 50 period.
- Long regime EMA/SMA: 200 period. User preference is EMA for the 200 moving average.
- RSI: 14 period, with 70 overbought, 30 oversold, and 50 centerline.
- Volume: raw volume compared with a 20-period volume SMA.
- Optional volume trend: OBV.
- MACD: standard 12, 26, 9.
- Bollinger Bands: 20-period basis, 2 standard deviations.
- Crypto volatility experiment: test 1.5 standard deviations as a tighter Bollinger setting.
- Short-term support/resistance: recent swing highs/lows on the active execution timeframe, generally the past 1 to 3 months.
- Long-term support/resistance: major weekly/monthly swing highs/lows, generally the past 6 to 12 months, plus psychological levels where relevant.

## Long/Bullish Breakout System

### Objective

Identify long trades in trending markets where price breaks or reclaims important resistance/support with multi-factor confirmation.

### Preferred Timeframes

- Daily or 4h for swing/positional trading.
- 1h can be evaluated for shorter-term versions.
- Weekly can be evaluated as a higher-timeframe filter.

### Long Entry Conditions

All entry rules should align at or near a short-term or long-term support/resistance level:

1. Trend confirmation:
   - Price above 20 EMA and 50 EMA.
   - 20 EMA above 50 EMA.
   - Prefer price and relevant index/category filter above the 200 EMA.
   - Rare mean-reversion longs below the 200 EMA may be considered only at major long-term support and should be handled as a separate variant.

2. RSI momentum:
   - RSI above 50 for bullish momentum.
   - RSI below 70 to avoid chasing overbought exhaustion.
   - Higher-quality setups may include bullish divergence at support: price makes a lower low while RSI makes a higher low.

3. Volume confirmation:
   - Volume above the 20-period volume SMA on breakout/reclaim.
   - Stronger breakout candidate if volume is 40 percent to 60 percent above the 20-period volume SMA.
   - Avoid low-volume breakouts.

4. MACD confirmation:
   - MACD line crosses above signal line.
   - Prefer MACD above zero.
   - Rising/widening histogram strengthens continuation thesis.

5. Bollinger Band context:
   - Break above upper band during breakout can confirm momentum expansion.
   - Touch/rejection of lower band at support can be used for a mean-reversion/reclaim variant.

6. Support/resistance trigger:
   - Price closes above short-term or long-term resistance.
   - For support reclaim variants, price confirms support with a close above the level.
   - Candlestick confirmation can be tested, for example bullish engulfing at support or breakout close above resistance.

### Example Long Setup

- Price breaks above short-term resistance, for example 100.
- 20 EMA above 50 EMA, both above 200 EMA.
- RSI around 55, bullish but not overbought.
- Volume spikes about 50 percent above volume SMA(20).
- MACD crosses above signal and is above zero.
- Price breaks above upper Bollinger Band, confirming breakout strength.

## Long Exit Logic

The user emphasized that an exit should not simply be the reverse of the entry signal. Entries are evidence of renewed momentum and continuation; exits should be evidence that bullish momentum has turned bearish or the trade has become trapped.

### Profit Targets

- Primary target: next significant short-term or long-term resistance level.
- Alternate target: 2R or 3R based on stop-loss distance.
- Extension target: hold a runner only while trend and momentum remain supportive.

### Stop-Loss

- Stop below the most recent swing low for longs.
- Stop below the breakout/reclaim level if that level should now act as support.
- Buffer may be placed outside the 20 EMA or lower Bollinger Band.
- Avoid placing stops so tight that normal volatility invalidates good trend trades.

### Trailing Exits

- Trail with 20 EMA: exit long if price closes below the 20 EMA.
- Fixed-percentage trailing stop can be tested, for example 2 percent.
- Larger trend-following variant should test the user 20 percent high/low regime rule.

### Indicator-Based Exits

- Exit long if RSI becomes overbought above 70 and bearish divergence appears.
- Exit long if MACD crosses below signal.
- Exit if volume falls below volume SMA(20) during the trend and price action weakens.
- Exit if a Bollinger breakout fails and price falls back inside the bands.

### Time-Based Exit

- Optional: exit if target is not reached within 5 to 10 bars on the execution timeframe.
- This should be tested carefully, because trend-following systems can be harmed by premature time exits.

## Bear Market / Short Breakdown System

### Objective

Invert the bullish framework to identify high-probability short trades during bear-market conditions or index-like downtrends.

### Bear Market Context

- Price below the 200 moving average on weekly or higher-timeframe chart.
- Major index/category trend below 200 EMA.
- Pullbacks to the 20 EMA, 50 EMA, or 200 EMA can be short-entry zones when they act as resistance.
- User preference: short trading is a different animal; indexes are preferred for short systems, usually 1h to 4h.

### Short Entry Conditions

All short-entry rules should align at support breakdown or resistance rejection:

1. Trend confirmation:
   - Price below 20 EMA and 50 EMA.
   - 20 EMA below 50 EMA.
   - Prefer price below 200 EMA.

2. RSI momentum:
   - RSI below 50 for bearish momentum.
   - RSI above 30 to avoid shorting into exhaustion.
   - Higher-quality setups may include bearish divergence at resistance: price makes a higher high while RSI makes a lower high.

3. Volume confirmation:
   - Volume above volume SMA(20) on breakdown.
   - OBV declining can strengthen bearish confirmation.
   - Avoid low-volume breakdowns.

4. MACD confirmation:
   - MACD crosses below signal line.
   - Prefer MACD below zero.
   - Widening histogram below zero strengthens bearish continuation.

5. Bollinger Band context:
   - Break below lower Bollinger Band during support breakdown can confirm bearish momentum.
   - Touch/rejection of upper Bollinger Band at resistance can support mean-reversion short entries.

6. Support/resistance trigger:
   - Price closes below short-term or long-term support.
   - Failed breakout or rejection at resistance can also trigger shorts.
   - Bearish candlestick confirmation can be tested, for example bearish engulfing, shooting star, or failed reclaim.

### Example Short Setup

- Price breaks below support, for example 50.
- 20 EMA below 50 EMA, both below 200 EMA.
- RSI around 45, bearish but not oversold.
- Volume spikes 60 percent above volume SMA(20).
- MACD crosses below signal and is below zero.
- Price breaks below lower Bollinger Band.
- Bearish engulfing candle confirms breakdown.

## Short Exit Logic

### Profit Targets

- Primary target: next significant support level.
- Alternate target: 2R or 3R based on stop-loss distance.

### Stop-Loss

- Stop above recent swing high.
- Stop above broken support if it should now act as resistance.
- Buffer may be placed outside the 20 EMA or upper Bollinger Band.

### Trailing Exits

- Trail with 20 EMA: exit short if price closes above the 20 EMA.
- Fixed-percentage trailing stop can be tested.

### Indicator-Based Exits

- Exit short if RSI goes below 30 and bullish divergence appears.
- Exit short if MACD crosses above signal or moves above zero.
- Exit if selling volume falls below volume SMA(20) and price stops trending down.
- Exit if price moves back inside Bollinger Bands after a lower-band breakdown.

### Time-Based Exit

- Optional: exit if target is not reached within 5 to 10 bars.

## User Portfolio and Regime Notes

These are important user-supplied rules and should be preserved as separate candidate exits or regime filters, not blended blindly into the entry rules.

### Long-Only Philosophy

Long-only systems should aim to remain in bullish conditions for as long as possible. Culling happens inside the system. The exit should be a clear sign that momentum has turned bearish, not simply the reverse of the entry.

### 200 EMA Index/Category Filter

If the relevant index or category trades below its 200 moving average, exit regardless of the individual stock or position signal.

For long trades:

- The index/category should be trading above the 200 EMA.
- The stock/asset should also be trading above the 200 EMA.
- This rule is intended to get the portfolio mostly out before major downside events.
- The user notes this exit tends to keep positions longer during whipsaws compared with faster exits.

For crypto translation:

- Test BTC or total-market proxy as a market-regime filter.
- For altcoin routes, test BTC/ETH 200 EMA as category risk-on/risk-off filter.
- Do not assume this improves futures strategies; validate through route sweeps.

### 20 Percent High/Low Regime Exit and Re-Entry Rule

User favorite rule:

- Trade only when a stock or index trades 20 percent above its most recent significant lowest low.
- Sell when the stock or index trades 20 percent below its most recent significant highest high.
- Re-enter after a 20 percent rally from a significant low.

Intent:

- Stay invested during prolonged long trends.
- Liquidate after a meaningful drawdown from a significant high.
- Buy back after a meaningful recovery from a significant low.
- This can allow a trader to sell high and buy back more units after a deep trend reset.

Research translation:

- Define "most recent significant low/high" explicitly.
- Candidate methods:
  - rolling N-bar low/high,
  - fractal swing high/low,
  - ATR-filtered swing point,
  - ZigZag-style threshold, without lookahead.
- Test as a regime filter and as an exit/re-entry module.
- Avoid lookahead bias when defining significant highs/lows.

### Whipsaw Trap Exit

Exit a trade that becomes trapped in a whipsaw scenario:

- Price locked between the buy entry and 1R profit.
- Price also remains near initial stop-loss zone.
- Trade fails to show continuation after entry.

User sizing note:

- "10 percent of equity in the trade normally."
- "1 to 1.5 percent of total capital" appears to refer to risk per trade, but this needs clarification before live sizing.

For Jesse research:

- Treat position sizing separately from signal rules.
- Default initial research risk should remain conservative.

### Short Trading Notes

Short trading is a separate system. User preference:

- Prefer indexes for shorts.
- Use 1h to 4h timeframes.
- Bear-market shock events can produce very large one-week opportunities.
- Example context mentioned: tariff shock.

Research implication:

- Keep bear-market short variants separate from long-only portfolio variants.
- Evaluate short systems on index-like crypto routes first, for example BTC/USDT and ETH/USDT perpetuals.
- Do not mix long-only equity portfolio logic with leveraged short-futures logic without separate testing.

## Risk Management Notes

- Risk no more than 1 percent to 2 percent of account per trade during initial research.
- Limit concurrent trades to avoid correlated exposure.
- Avoid low-volume periods and major news unless the strategy explicitly targets volatility shocks.
- Avoid choppy markets where RSI oscillates around 50 and MACD is flat.
- Optional ADX filter below 20 can be tested as a chop filter, but should not be added unless it improves robustness.
- Bear-market leverage should be conservative. Test 1x, 2x, 3x first. Consider 5x only if drawdown, stop distance, and liquidation buffer justify it.

## Optimization Ideas to Preserve

- Test MA periods:
  - Standard: 20/50/200.
  - Faster bear-market/crypto variant: 10/30/200.
- Test RSI thresholds:
  - Standard: long above 50 but below 70, short below 50 but above 30.
  - Aggressive regimes: 40/60 bands.
- Test Bollinger settings:
  - Standard: 20 period, 2 standard deviations.
  - Volatile crypto: 20 period, 1.5 standard deviations.
- Test timeframes:
  - 1h, 4h, daily.
- Test route grid:
  - BTC-USDT, ETH-USDT, SOL-USDT perpetual futures first.
- Test leverage grid:
  - 1x, 2x, 3x.
  - 5x only for short-horizon variants with proven stop/liquidation buffer.

## Jesse Investigation Brief

Future Gas Town/Jesse workers should convert these notes into separate, testable candidates:

### Candidate A: Long Trend-Momentum Breakout

- Archetype: trend continuation / breakout.
- Market: crypto futures, long-only first.
- Entry: resistance breakout with 20/50/200 EMA alignment, RSI momentum, volume spike, MACD confirmation, and Bollinger expansion.
- Exit: next S/R or R-multiple target, 20 EMA trail, MACD/RSI deterioration, failed Bollinger breakout.
- Regime filter: asset and market proxy above 200 EMA.

### Candidate B: Long Trend Re-Entry With 20 Percent Regime Rule

- Archetype: trend following / regime re-entry.
- Entry: 20 percent rally from significant low, with 200 EMA risk-on filter and momentum confirmation.
- Exit: 20 percent drawdown from significant high, or 200 EMA category/index filter breach.
- Key risk: lookahead bias in significant high/low definition.

### Candidate C: Bear Market Short Breakdown

- Archetype: bearish breakdown / pullback rejection.
- Market: index-like crypto futures routes first.
- Entry: support breakdown or resistance rejection with bearish EMA alignment, RSI below 50 but not oversold, volume spike, MACD below zero/cross down, and lower Bollinger Band break or upper-band rejection.
- Exit: next support, R-multiple target, 20 EMA trail, RSI bullish divergence, MACD recovery, failed breakdown.
- Regime filter: price below 200 EMA and broader market proxy below 200 EMA.

### Candidate D: Shock-Event Short Variant

- Archetype: volatility shock continuation.
- Market: BTC/ETH perpetuals, 1h/4h.
- Entry: high-volume breakdown after macro shock, lower-band expansion, bearish MACD, and S/R break.
- Exit: tight time-based or volatility contraction exit.
- Key risk: event-specific overfitting.

## Backtest and Review Requirements

Every serious candidate derived from these notes should report:

- Edge thesis.
- Target regime and failure regime.
- Exact Jesse implementation notes.
- Support/resistance construction method.
- Entry and exit rule variants.
- Hyperparameters.
- Asset/timeframe/leverage route grid.
- Exact backtest commands.
- Net profit.
- Profit factor.
- Expectancy.
- Max drawdown.
- Trade count.
- Parameter sensitivity.
- Liquidation buffer and leverage notes.
- Final verdict: reject, revise, hpo-candidate, or paper-trade candidate.


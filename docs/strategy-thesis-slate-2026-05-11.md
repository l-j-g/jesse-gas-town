# Strategy Thesis Slate - 2026-05-11

Issue: `jt-cin.1`

This document is research only. It is not personalized financial advice and it is not a live-deployment recommendation.

## Shared Assumptions

- Market: liquid crypto perpetual futures only.
- Asset universe: start with `BTC-USDT`, `ETH-USDT`, and `SOL-USDT`; narrow per thesis when lower-liquidity behavior becomes a risk.
- Route policy: primary execution timeframe plus one higher-timeframe regime filter when the thesis depends on trend context.
- Leverage candidates: start with `1x`, `2x`, and `3x`; allow `5x` only for short-hold families after liquidation-buffer review.
- Position sizing: fixed fractional risk per trade sized from stop distance, with baseline risk per trade in the `0.25%` to `0.75%` equity range.
- Validation order: Jesse correctness review, baseline backtest, route sweep, nearby-parameter sensitivity check, then verdict.
- Acceptance guardrails: prefer at least `100` trades for trust, profit factor above `1.2`, positive expectancy after fees, and drawdown proportionate to net profit.

## Thesis 1: KAMA-ADX Trend Continuation

- Family: trend continuation
- Edge thesis: when a liquid perpetual is already trending on the higher timeframe and shallow retracements keep failing, re-acceleration entries have better expectancy than buying the first impulse candle.
- Target regime: `4h` and `1h` trend alignment, positive KAMA slope, widening `DI+` or `DI-`, and ADX rising out of a non-trending state.
- Failure regime: alternating closes around the trend filter, ADX decay, and repeated wick-driven reversals that show poor directional persistence.
- Measurement tools: `kama`, `adx`, `di`, `supertrend`, `atr`
- Route assumptions: `BTC/ETH/SOL` perpetuals, `30m` execution, `4h` regime filter, `1x/2x/3x`
- Risk model: ATR stop beyond the invalidation swing, partial at `1R` or prior impulse high/low, trail the remainder with KAMA or SuperTrend.
- First validation plan: implement with only KAMA length, ADX threshold, and ATR stop multiple as hyperparameters; run baseline routes on `BTC`, `ETH`, and `SOL`, then test nearby ADX and stop values for collapse risk.
- Weakest risk: late entries on mature trends can convert continuation logic into top-ticking.
- Verdict: `revise`

## Thesis 2: Compression Breakout With Range Acceptance

- Family: breakout
- Edge thesis: volatility compression near a clean structure boundary often resolves into directional expansion, but only breakouts that hold outside the prior range are worth paying for.
- Target regime: tight Bollinger or squeeze width, stable range highs/lows, then a breakout candle that is followed by acceptance instead of immediate rejection.
- Failure regime: news-like spikes, one-bar breakouts with no follow-through, and conditions where price repeatedly re-enters the prior range.
- Measurement tools: `donchian`, `bollinger_bands_width`, `ttm_squeeze`, `atr`, `volume`
- Route assumptions: `BTC/ETH/SOL` perpetuals, `15m` execution, optional `1h` structure filter, `1x/2x`
- Risk model: stop back inside the broken range, time stop if expansion does not persist within a few bars, scale out into `2R` and trail only if range extension remains orderly.
- First validation plan: compare a plain Donchian breakout baseline against the compression-filtered version; then sweep assets and test sensitivity around squeeze-width and hold-confirmation thresholds.
- Weakest risk: false breakouts cluster during chop and can erase many small gains quickly.
- Verdict: `revise`

## Thesis 3: Pullback Continuation Into Dynamic Trend Support

- Family: pullback continuation
- Edge thesis: strong trends often resume after controlled pullbacks into dynamic support or resistance once short-term momentum resets without breaking the higher-timeframe regime.
- Target regime: higher-timeframe trend intact, pullback depth contained, RSI reset out of overbought or oversold without flipping the regime, and trend strength still acceptable.
- Failure regime: pullbacks that become structural reversals, regime filters that flatten, and repeated failed bounces from the same support zone.
- Measurement tools: `ema`, `kama`, `rsi`, `adx`, `atr`
- Route assumptions: `BTC/ETH` perpetuals first, `15m` or `30m` execution, `4h` regime filter, `1x/2x/3x`
- Risk model: stop beyond the pullback swing, first profit target at the prior impulse extreme, optional runner for measured-move continuation.
- First validation plan: test shallow, medium, and deep pullback bands separately; compare RSI reset thresholds and verify whether continuation still works after small parameter moves.
- Weakest risk: deep pullbacks can look statistically similar to reversals until the loss is already booked.
- Verdict: `revise`

## Thesis 4: Trend Flag Break After Controlled Consolidation

- Family: pullback continuation
- Edge thesis: after a strong impulse, micro-consolidations that contract volatility and hold above trend support can offer better risk-adjusted entries than chasing the original move.
- Target regime: fresh impulse, short sideways flag, low realized volatility inside the flag, and breakout in the direction of the original impulse while higher-timeframe slope stays intact.
- Failure regime: flags that widen instead of tighten, exhaustion moves with no real trend context, and chop that repeatedly tags both sides of the flag.
- Measurement tools: `ema`, `linearreg_slope`, `chop`, `bollinger_bands_width`, `atr`
- Route assumptions: `ETH/SOL` perpetuals first, `5m` or `15m` execution, `1h` trend context, `1x/2x`
- Risk model: stop beyond the opposite side of the flag, first target at measured flag extension, time stop if breakout momentum stalls quickly.
- First validation plan: compare continuation entries at the flag break against immediate post-impulse entries, then run parameter perturbation around flag width and trend-slope thresholds.
- Weakest risk: low-timeframe flags are prone to overfitting and slippage drag.
- Verdict: `revise`

## Thesis 5: Balanced-Range Mean Reversion

- Family: mean reversion
- Edge thesis: when trend strength is weak and volatility is stable, repeated excursions from balance to short-term extremes often revert back toward value faster than trend-following systems can react.
- Target regime: high chop, low or falling ADX, repeated respect of range boundaries, and no evidence of directional expansion.
- Failure regime: emerging trends, regime shifts from range to breakout, and expanding ATR that invalidates the assumption of stable balance.
- Measurement tools: `bollinger_bands`, `zscore`, `rsi`, `willr`, `chop`, `vwap`
- Route assumptions: `BTC/ETH` perpetuals, `5m` or `15m` execution, no leverage above `2x`
- Risk model: hard stop outside the range extreme, first target at VWAP or mid-band, optional second target at the opposite side of value only when the range has multiple prior rotations.
- First validation plan: run a baseline on balanced periods, then explicitly test degradation during breakout-heavy months; verify that fees do not consume the edge on lower timeframes.
- Weakest risk: the strategy dies abruptly when balance transitions into directional expansion.
- Verdict: `revise`

## Thesis 6: Failed Breakout Fade Back Into Value

- Family: mean reversion / exhaustion reversal hybrid
- Edge thesis: breakout attempts that lose acceptance and close back inside the prior range often travel quickly toward mid-range value because trapped breakout traders become the fuel for the reversal.
- Target regime: clean range boundary, breakout beyond that boundary, then immediate rejection back into the prior value area with momentum loss.
- Failure regime: true trend days where the first rejection is only a retest before continuation, and thin-liquidity candles that make the rejection signal noisy.
- Measurement tools: `donchian`, `volume`, `willr`, `rsi`, `atr`
- Route assumptions: `BTC/ETH` perpetuals, `15m` execution, `1x/2x`
- Risk model: stop beyond the failed-break extreme, target VWAP or range midpoint first, extend to opposite range boundary only if the session stays balanced.
- First validation plan: compare rejection-close entries against simpler opposite-band fades; test whether the edge survives after fees and after small changes in re-entry confirmation.
- Weakest risk: one strong trend day can create multiple consecutive failed-fade losses.
- Verdict: `revise`

## Thesis 7: Volatility Expansion After Squeeze Release

- Family: volatility expansion
- Edge thesis: extreme compression tends to precede outsized directional movement, and the first expansion leg can be captured if the strategy waits for both volatility release and directional confirmation.
- Target regime: low realized volatility percentile, sustained squeeze state, then ATR expansion plus directional structure break.
- Failure regime: noisy squeezes inside broad chop, rapid snap-back after the first expansion candle, and event-driven spikes that distort volatility readings.
- Measurement tools: `ttm_squeeze`, `bollinger_bands_width`, `atr`, `supertrend`, `di`
- Route assumptions: `BTC/ETH/SOL` perpetuals, `15m` or `30m` execution, `1x/2x`
- Risk model: stop near the squeeze midpoint or opposite squeeze boundary, partial at `1.5R` to `2R`, trail only if ATR expansion remains elevated.
- First validation plan: compare expansion entries with and without trend confirmation; route-sweep assets and timeframes to find whether the family prefers slower `30m` expansion or faster `15m` release.
- Weakest risk: breakout and expansion logic can degenerate into buying volatility after the profitable part has already passed.
- Verdict: `revise`

## Thesis 8: Exhaustion Reversal From Volatility Extreme

- Family: exhaustion reversal
- Edge thesis: parabolic extensions away from the mean often snap back sharply once momentum fails and the first confirmed reversal prints near an extreme.
- Target regime: stretched move away from value, volatility spike, momentum divergence or recovery from a deeply extended oscillator state, and reversal confirmation near a local blowoff point.
- Failure regime: persistent trend acceleration, liquidation cascades that keep extending, and attempts to fade moves before confirmation.
- Measurement tools: `bollinger_bands`, `lrsi`, `willr`, `atr`, `vwap`
- Route assumptions: `BTC/ETH` perpetuals, `5m` or `15m` execution, `1x` initially and `2x` only if route review proves liquidation buffer is ample
- Risk model: entry only after confirmation close, stop beyond the exhaustion extreme, first target at VWAP or KAMA, optional runner to prior structure shelf.
- First validation plan: run strictly confirmed entries against a looser early-fade variant, then check whether the higher win-rate version is actually inferior once trend-overrun losses are counted.
- Weakest risk: countertrend fading can look clever in samples and then fail catastrophically during true expansion.
- Verdict: `revise`

## Recommended Wave 1 Build Priority

1. Thesis 1: KAMA-ADX Trend Continuation
2. Thesis 2: Compression Breakout With Range Acceptance
3. Thesis 3: Pullback Continuation Into Dynamic Trend Support
4. Thesis 7: Volatility Expansion After Squeeze Release

These four give the cleanest first wave because they cover separate families, map directly onto Jesse-native indicators, and can be tested on medium-liquidity futures routes without relying on exotic data.

## Overall Verdict

All eight theses are pre-implementation research candidates. The correct next status for each is `revise` until a Jesse-native implementation, route sweep, and robustness review produce evidence for `hpo-candidate` or `paper-trade candidate`.

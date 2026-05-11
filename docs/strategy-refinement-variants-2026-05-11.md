# Wave 1 Refinement Variants - 2026-05-11

Issue: `jt-cin.3`

This document is research only. It is not personalized financial advice and it is not a live-trading recommendation.

Scope rule: every refinement below changes exactly one coherent edge component. No indicator-stacking variants are proposed without a market hypothesis.

## Shared Evaluation Frame

- Market: liquid crypto perpetual futures only.
- Primary assets: `BTC-USDT`, then `ETH-USDT` and `SOL-USDT` when the BTC baseline is coherent.
- Validation order: Jesse correctness review, baseline backtest, route sweep, nearby-parameter sensitivity check, then verdict.
- Baseline guardrails: prefer profit factor above `1.2`, positive expectancy after fees, drawdown proportionate to net profit, and enough trades to trust the sample.
- Current status for all originals and refinements: `revise` until backtested.

## KAMA_TrendFollowing

### Original: KAMA Trend Continuation

- Thesis: when the higher-timeframe trend is already established, continuation entries after directional re-alignment should outperform countertrend participation.
- Changed component: none; baseline reference.
- Expected improvement: establish the control result for later A/B comparisons.
- Targeted tests: run the baseline on `BTC-USDT` futures `15m` for `2022-01-01` through `2022-12-31`, then sweep `30m` and `1h`, then repeat on `ETH-USDT` and `SOL-USDT` if the BTC route is coherent.
- Weakest risk: aggressive trend thresholds may overtrade in alternating trend/no-trend transitions.
- Verdict: `revise`

### Variant: KAMA Chop Stand-Down

- Changed component: regime filter.
- Thesis: the baseline should stand down when KAMA slope persists but directional strength is too weak, because chop around the trend line is where continuation logic pays the most whipsaw tax.
- Expected improvement: lower false-entry density, lower drawdown, and better profit factor in flat or rotating periods.
- Targeted tests: A/B against the original on `BTC-USDT` futures `15m` for `2022-01-01` through `2022-12-31`; inspect range-heavy months separately; perturb the regime-strength threshold one step tighter and one step looser to check for collapse.
- Weakest risk: may remove too many trades and blunt the strong baseline trade count.
- Verdict: `revise`

### Variant: KAMA Pullback Reclaim

- Changed component: entry trigger.
- Thesis: waiting for a shallow pullback reclaim into the trend should outperform chasing the first re-acceleration candle when a mature move is already extended.
- Expected improvement: better average entry price, reduced late-trend chasing, and improved expectancy even if trade count falls.
- Targeted tests: A/B against the original on `BTC-USDT` futures `15m` and `30m` for `2022-01-01` through `2022-12-31`; compare entry efficiency, average hold time, and win/loss asymmetry.
- Weakest risk: may miss runaway continuation legs that never retest.
- Verdict: `revise`

### Variant: KAMA ATR Trail Scale-Out

- Changed component: trade management.
- Thesis: taking a partial at the first asymmetric payout point and trailing the remainder with the trend measure should reduce winner giveback without cutting off strong trend legs too early.
- Expected improvement: smoother equity curve, improved realized win size retention, and smaller round-trip reversals after open profit.
- Targeted tests: A/B against the original on `BTC-USDT` futures `15m` for `2022-01-01` through `2022-12-31`; compare average winner size, open-to-closed profit giveback, and max drawdown; rerun on `ETH-USDT` only if the BTC result improves.
- Weakest risk: partial exits can reduce the upside of the strongest continuation runs.
- Verdict: `revise`

## SuperScalper

### Original: Trend-Aligned Scalper

- Thesis: lower-timeframe scalps work best when fast execution entries agree with the higher-timeframe trend and directional strength is already present.
- Changed component: none; baseline reference.
- Expected improvement: establish the fee- and slippage-adjusted baseline before refining.
- Targeted tests: run the baseline on `BTC-USDT` futures `15m` for `2022-01-01` through `2022-12-31`, then sweep `5m` and `30m`; repeat on `ETH-USDT` and `SOL-USDT`; compare outcomes under conservative fee and slippage assumptions before allowing leverage above `3x`.
- Weakest risk: the edge may decay quickly once trading costs and lower-timeframe noise are included.
- Verdict: `revise`

### Variant: SuperScalper Volatility Floor

- Changed component: regime filter.
- Thesis: a scalper should only trade when short-term volatility is alive enough to pay for fees, because dead tapes generate many technically valid but economically weak signals.
- Expected improvement: better fee-adjusted expectancy, fewer low-range losses, and reduced churn.
- Targeted tests: A/B against the original on `BTC-USDT` futures `5m` and `15m` for `2022-01-01` through `2022-12-31`; compare net profit after fees, trades per day, and profit factor; perturb the volatility floor one step in each direction.
- Weakest risk: may filter out too much activity and damage the sample size advantage.
- Verdict: `revise`

### Variant: SuperScalper Pullback Entry

- Changed component: entry trigger.
- Thesis: entering on a brief pullback back into the fast trend structure should outperform taking immediate continuation signals after the move is already underway.
- Expected improvement: better fills, less slippage, and fewer entries at local intrabar extremes.
- Targeted tests: A/B against the original on `BTC-USDT` futures `5m` and `15m` for `2022-01-01` through `2022-12-31`; compare average entry distance from subsequent excursion, stop-out frequency, and trade expectancy.
- Weakest risk: the best momentum bursts may never retrace enough to trigger.
- Verdict: `revise`

### Variant: SuperScalper Time-Stop Scratch

- Changed component: trade management.
- Thesis: when a scalp does not begin working within a short bar window, the thesis is usually wrong and the trade should be scratched before friction turns a small mistake into a full loss.
- Expected improvement: smaller average loser, lower holding-time drag, and less capital bleed during stalled sessions.
- Targeted tests: A/B against the original on `BTC-USDT` futures `5m` and `15m` for `2022-01-01` through `2022-12-31`; compare loser duration, fee-adjusted expectancy, and drawdown clustering; rerun only the stronger timeframe on `ETH-USDT`.
- Weakest risk: may cut eventual winners that start slowly before expanding.
- Verdict: `revise`

## TrendWaveRiderV2

### Original: ADX-CCI Trend Pullback

- Thesis: strong directional regimes often resume after controlled pullbacks when trend strength remains intact and short-term momentum resets out of exhaustion.
- Changed component: none; baseline reference.
- Expected improvement: establish whether the fixed pullback logic is already strong enough to justify route work before exposing more knobs.
- Targeted tests: run the baseline on `BTC-USDT` futures `15m` for `2024-01-01` through `2024-12-31`, then sweep `30m` and `1h`; repeat on `ETH-USDT` and `SOL-USDT` only if the primary BTC route is coherent.
- Weakest risk: the strategy may miss runaway trends or overfit one pullback depth.
- Verdict: `revise`

### Variant: TrendWaveRiderV2 Shallow Pullback Band

- Changed component: entry trigger.
- Thesis: in very strong ADX regimes, continuation often resumes from shallow pullbacks, so requiring a deeper reset can leave the strategy under-invested in the best trend phases.
- Expected improvement: higher participation in fast continuation legs and a healthier trade count without changing the regime thesis.
- Targeted tests: A/B against the original on `BTC-USDT` futures `15m` and `30m` for `2024-01-01` through `2024-12-31`; compare trade count, average winner size, and whether added trades degrade profit factor.
- Weakest risk: shallower entries can increase buying into exhaustion instead of pullback completion.
- Verdict: `revise`

### Variant: TrendWaveRiderV2 Higher-Timeframe Trend Guard

- Changed component: regime filter.
- Thesis: requiring higher-timeframe trend alignment before acting on the pullback reset should cut the most expensive countertrend bounce attempts.
- Expected improvement: lower drawdown and better signal quality during regime transitions or noisy consolidations.
- Targeted tests: A/B against the original on `BTC-USDT` futures `15m` with a higher-timeframe trend context for `2024-01-01` through `2024-12-31`; inspect adverse excursions and failed-bounce clusters by quarter; rerun on `ETH-USDT` only if BTC improves.
- Weakest risk: extra filtering may make the already sparse baseline too selective.
- Verdict: `revise`

### Variant: TrendWaveRiderV2 Failure Exit

- Changed component: stop/TP logic.
- Thesis: if price fails to re-accelerate within a short window after the pullback entry, the setup is behaving more like a reversal than a continuation and the exit should tighten early.
- Expected improvement: smaller full-stop losses and cleaner protection against deep pullbacks that become regime breaks.
- Targeted tests: A/B against the original on `BTC-USDT` futures `15m` for `2024-01-01` through `2024-12-31`; compare average loser size, max drawdown, and the share of trades that never reach positive excursion before stopping.
- Weakest risk: early failure logic can eject valid trades that need more time to develop.
- Verdict: `revise`

## Turtle V2

### Original: Donchian Breakout With Trend/Chop Gates

- Thesis: clean structure breaks in directional markets should outperform range trading when trend and chop filters keep the strategy out of the noisiest breakout traps.
- Changed component: none; baseline reference.
- Expected improvement: establish whether the current breakout gate is already selective enough or under-traded before introducing refinements.
- Targeted tests: run the baseline on `BTC-USDT` futures `1h` for `2022-01-01` through `2022-12-31`, then sweep `30m` and `2h`; repeat on `ETH-USDT` and `SOL-USDT`; review trade density before expanding leverage beyond `3x`.
- Weakest risk: false breakouts in range conditions can still dominate the equity curve.
- Verdict: `revise`

### Variant: Turtle V2 Compression Confirmation

- Changed component: entry trigger.
- Thesis: breakout entries should work better when the channel break follows visible compression, because structure expansion from stored energy is more durable than random range-edge pokes.
- Expected improvement: fewer failed breakouts, higher average trade quality, and improved profit factor even with lower trade count.
- Targeted tests: A/B against the original on `BTC-USDT` futures `30m` and `1h` for `2022-01-01` through `2022-12-31`; inspect post-break follow-through distance and failed breakout frequency; rerun the better timeframe on `ETH-USDT`.
- Weakest risk: waiting for compression may skip the most obvious trend continuation breakouts.
- Verdict: `revise`

### Variant: Turtle V2 Failed-Break Time Stop

- Changed component: trade management.
- Thesis: a valid breakout should show directional follow-through quickly, so trades that stall immediately after entry should be cut before they decay into full breakout failures.
- Expected improvement: lower average loss, lower drawdown, and better capital efficiency during choppy periods.
- Targeted tests: A/B against the original on `BTC-USDT` futures `1h` for `2022-01-01` through `2022-12-31`; compare loser duration, drawdown, and breakout failure clusters; then check whether the same behavior holds on `30m`.
- Weakest risk: some durable breakouts begin with a retest and may be exited too early.
- Verdict: `revise`

### Variant: Turtle V2 Volatility-Scaled Sizing

- Changed component: sizing.
- Thesis: breakout signals fired on unusually large bars should carry smaller size because they are closer to exhaustion and require more adverse room than ordinary channel breaks.
- Expected improvement: reduced tail-loss severity without rewriting the breakout entry or exit logic.
- Targeted tests: A/B against the original on `BTC-USDT` futures `1h` for `2022-01-01` through `2022-12-31`; compare return-to-drawdown ratio, loss distribution, and leverage tolerance at `1x`, `2x`, and `3x`.
- Weakest risk: reducing size on large breakout bars may mute the very trades that drive the strategy's upside.
- Verdict: `revise`

## Recommended First Backtest Queue

1. `KAMA Pullback Reclaim`
2. `SuperScalper Time-Stop Scratch`
3. `TrendWaveRiderV2 Shallow Pullback Band`
4. `Turtle V2 Failed-Break Time Stop`

These four are the cleanest first queue because each isolates one stress point already called out in intake: late-trend chasing, fee drag, missed runaway trends, and failed breakout losses.

## Overall Verdict

All four originals remain valid desk baselines, and each now has a small refinement set that can be tested without changing the family thesis. The correct next status for the originals and all refinements is `revise` until the Backtesting Desk runs correctness checks, baseline backtests, and route comparisons.

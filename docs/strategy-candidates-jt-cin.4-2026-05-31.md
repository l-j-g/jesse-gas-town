# Strategy Candidates - 2026-05-31

Issue: `jt-cin.4`

This document is research and implementation context only. It is not personalized financial advice and it is not a live-trading recommendation.

## Candidate 1: `KamaAdxPullback`

- Thesis: persistent directional moves tend to offer better entries after a shallow pullback reclaim than on the initial impulse, especially when KAMA slope and DI/ADX still confirm trend strength.
- Archetype: trend / pullback continuation
- Target regime: directional futures tape with rising KAMA, ADX above the stand-up threshold, and a brief pullback that tags the adaptive trend line before a momentum reclaim.
- Failure regime: maturing trends that are already exhausted, alternating closes around KAMA, or weak ADX readings that imply chop rather than continuation.
- Entry model: KAMA trend alignment plus pullback touch and reclaim through the prior bar extreme.
- Exit model: ATR-buffered invalidation beyond the pullback swing and fixed `R`-multiple target.
- First backtest route: `BTC-USDT` perpetual futures, `15m`, calendar year `2024`, leverage candidates `1x/2x`.

## Candidate 2: `FailedBreakoutValueFade`

- Thesis: breakouts that lose acceptance and close back inside a stable range often mean revert quickly toward value as trapped breakout traders unwind.
- Archetype: failed breakout / mean reversion
- Target regime: low-ADX balance, Donchian-defined structure edges, and a rejection candle that closes back inside the range after an excursion through the boundary.
- Failure regime: true trend expansion days, news shocks, or volatility regimes where the first rejection is only a retest before continuation.
- Entry model: failed Donchian breakout with Williams %R still stretched and price reclaiming the range boundary.
- Exit model: ATR-buffered stop outside the failed-break extreme and first value target at the closest favorable VWAP or Donchian midpoint.
- First backtest route: `BTC-USDT` perpetual futures, `15m`, calendar year `2022`, leverage candidates `1x/2x`.

## Next Evaluation Step

- Run correctness and baseline backtests under `jt-cin.5` before any HPO or leverage expansion.

# Jesse.Trade Reference Intake - 2026-05-11

## Summary

This was a static intake and ranking pass over the Jesse.Trade example strategy catalog and the private account-downloaded source folder.

No Jesse backtests or optimizations were run in this pass. Private strategy source was inspected structurally only and was not committed or quoted.

## Source Coverage

- Captured source: 23 of 24 strategies.
- Premium captured: 7 of 7.
- Missing source: DonchianATRTrend.

## Captured Sets

Free captured examples:
TemaTrendFollowing, ADXWilliamsStrategy, KAMA_TrendFollowing, TurtleAI, CloudScalper, TrendSwingTrader V1, AlligatorAI, IchimokuCloud, MeanReversionRSI, Trend Following, RSI Trend, TrendWaveRider.

Premium captured examples:
Turtle V2, TrendWaveRiderV2, Turtle V3, AlligatorV2, TrendSwingTrader V2, SuperScalper, Slow Trend Following.

Unknown-tier captured examples:
EMBIA, MACD + EMA, Golden Cross Strategy, IFR2.

## Backtesting Desk Ranking

1. KAMA_TrendFollowing
   - Best first desk candidate.
   - Public metrics: 147.28% PNL, Sharpe 2.08, max DD -23.55%, 128 trades.
   - Proposed route sweep: BTC/ETH/SOL futures, 15m/30m/1h, 1x/2x/3x.
   - Weakest risk: aggressive trend thresholds may be regime-specific.

2. SuperScalper
   - Best high-trade premium candidate.
   - Public metrics: 59.41% PNL, Sharpe 1.93, max DD -12.47%, 132 trades.
   - Proposed route sweep: BTC/ETH/SOL, 5m/15m/30m, 1x/2x/3x/5x with 5x gated by liquidation checks.
   - Weakest risk: scalper edge may decay fastest under fees/slippage.

3. TrendWaveRiderV2
   - Strong trend-pullback candidate.
   - Public metrics: 108.27% PNL, Sharpe 2.18, max DD -19.59%, 67 trades.
   - Proposed route sweep: BTC/ETH/SOL, 15m/30m/1h, 1x/2x/3x.
   - Weakest risk: may miss runaway trends and overfit pullback depth.

4. Turtle V2
   - Best breakout baseline.
   - Public metrics: 118.23% PNL, Sharpe 1.79, max DD -16.61%, 68 trades.
   - Proposed route sweep: BTC/ETH/SOL, 30m/1h/2h, 1x/2x/3x.
   - Weakest risk: false breakouts in range conditions.

5. TemaTrendFollowing
   - High-upside but sizing-risky candidate.
   - Public metrics: 309.26% PNL, Sharpe 2.97, max DD -25.99%, 67 trades.
   - Proposed route sweep: BTC/ETH, optional SOL, 15m/30m/1h, 1x/2x/3x only.
   - Weakest risk: public result looks amplified by aggressive sizing and wide ATR stops.

6. ADXWilliamsStrategy
   - Simpler trend/exhaustion hybrid worth desk time.
   - Public metrics: 210.62% PNL, Sharpe 1.98, max DD -25.20%, 56 trades.
   - Proposed route sweep: BTC/ETH, 15m/30m/1h, 1x/2x/3x.
   - Weakest risk: drawdown is too large relative to trade count to trust without reruns.

7. TrendSwingTrader V2
   - Clean slower swing candidate, but sparse.
   - Public metrics: 70.80% PNL, Sharpe 1.95, max DD -10.73%, 30 trades.
   - Proposed route sweep: BTC/ETH, 2h/4h/6h, 1x/2x.
   - Weakest risk: trade count is too low for optimization trust.

8. AlligatorV2
   - Secondary premium candidate.
   - Public metrics: 90.14% PNL, Sharpe 1.77, max DD -13.89%, 37 trades.
   - Proposed route sweep: BTC/ETH, 30m/1h/2h, 1x/2x/3x.
   - Weakest risk: low sample size despite decent drawdown.

## Deprioritized

Turtle V3, TurtleAI, TrendWaveRider, AlligatorAI, CloudScalper, IchimokuCloud, Trend Following, and TrendSwingTrader V1 are useful references but weaker than the first desk wave.

MeanReversionRSI, Slow Trend Following, EMBIA, RSI Trend, and IFR2 should not enter the early desk wave because public samples are too small or too narrow.

MACD + EMA and Golden Cross Strategy should be treated as reject from intake because the public results are poor.

DonchianATRTrend is blocked until its private source is recovered.

## Recommended Next Step

Run Backtesting Desk first against:

1. KAMA_TrendFollowing
2. SuperScalper
3. TrendWaveRiderV2
4. Turtle V2

For each, run correctness review, baseline backtest, asset/timeframe route sweep, leverage guardrail review, then HPO gate.

## Wave 1 Candidate Prep

### 1) KAMA_TrendFollowing

- Archetype: trend following with higher-timeframe confirmation.
- Baseline route: BTC-USDT futures first, then ETH-USDT and SOL-USDT if the BTC baseline is coherent.
- Timeframes: 15m, 30m, 1h.
- Leverage route: 1x, 2x, 3x.
- Hyperparameters: none exposed; the strategy currently relies on hard-coded thresholds and cooldown logic.
- Correctness notes: futures order placement is Jesse-valid because entries flow through `self.buy` / `self.sell` and exits are attached after fill. The main prep blocker is that the control surface is fixed in code, so the desk has little parameter room until the thresholds are surfaced as hyperparameters.

### 2) SuperScalper

- Archetype: trend-aligned scalper using short- and higher-timeframe trend agreement.
- Baseline route: BTC-USDT futures first, then ETH-USDT and SOL-USDT.
- Timeframes: 5m, 15m, 30m.
- Leverage route: 1x, 2x, 3x, with 5x only after liquidation-buffer review.
- Hyperparameters:
  - `stop_loss`
  - `take_profit`
  - `adx_threshold`
  - `long_term_ma_period`
- Correctness notes: Jesse lifecycle usage is mostly clean. Entry cancellation is explicit, exits are set after fill, and the strategy has a compact hyperparameter set. The main review item is whether the scalper edge survives fees and slippage across the lower-timeframe sweep.

### 3) TrendWaveRiderV2

- Archetype: trend-pullback hybrid with ADX and CCI confirmation.
- Baseline route: BTC-USDT futures first, then ETH-USDT and SOL-USDT.
- Timeframes: 15m, 30m, 1h.
- Leverage route: 1x, 2x, 3x.
- Hyperparameters: none exposed; the current logic uses fixed trend and oscillator thresholds.
- Correctness notes: the package is structurally Jesse-valid for futures, but it is another fixed-logic candidate with no tuning surface. That makes it a reference input more than an HPO-ready package until the desk decides whether to surface the threshold constants.

### 4) Turtle V2

- Archetype: Donchian breakout with trend and chop filters.
- Baseline route: BTC-USDT futures first, then ETH-USDT and SOL-USDT.
- Timeframes: 30m, 1h, 2h.
- Leverage route: 1x, 2x, 3x.
- Hyperparameters:
  - `adx_threshold`
  - `chop_threshold`
  - `stop_loss`
  - `long_term_ma_period`
  - `donchian_period`
- Correctness notes: the strategy uses Jesse-native lifecycle hooks and a trailing stop update path, so it is a valid futures package. The prep risk is that the breakout gate is fairly strict and may need route-specific verification to avoid an under-traded baseline.

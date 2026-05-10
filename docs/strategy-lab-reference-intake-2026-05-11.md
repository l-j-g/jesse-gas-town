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

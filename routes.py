from jesse.enums import exchanges


routes = [
    {
        'exchange': exchanges.BINANCE_PERPETUAL_FUTURES,
        'symbol': 'BTC-USDT',
        'timeframe': '1h',
        'strategy': 'BaselineMaTrend',
    },
]

extra_candles = []

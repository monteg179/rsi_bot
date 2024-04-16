import httpx
from pandas import (
    DataFrame,
)
from pandas_ta import (
    rsi,
)


class Bybit:

    @staticmethod
    async def get_kline(symbol: str, interval: str, limit: int = 200):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url='https://api-testnet.bybit.com/v5/market/kline',
                params={
                    'category': 'linear',
                    'symbol': symbol,
                    'interval': interval,
                    'limit': limit,
                }
            )
            if response.status_code == httpx.codes.OK:
                return response.json()

    @staticmethod
    def get_kline_rsi(json: dict, length: int) -> float:
        candles = json['result']['list']
        data = DataFrame(
            data={'close': [float(candle[4]) for candle in candles[::-1]]}
        )
        return rsi(data.close, length).iloc[-1]

    @staticmethod
    async def get_historical_volatility(
        category: str,
        baseCoin: str,
        period: int
    ):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=('https://api-testnet.bybit.com/v5/market/'
                     'historical-volatility'),
                params={
                    'category': category,
                    'baseCoin': baseCoin,
                    'period': period
                }
            )
        if response.status_code == httpx.codes.OK:
            return response.json()

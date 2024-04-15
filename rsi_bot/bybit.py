import httpx


class Bybit:

    @staticmethod
    async def get_kline(symbol: str, interval: str, limit: int):
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

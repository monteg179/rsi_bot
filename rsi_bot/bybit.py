import asyncio
from typing import (
    Any,
    Self,
)

import httpx
from pandas import (
    DataFrame,
)
import pandas_ta

from rsi_bot import settings

DEBUG = settings.DotEnv().debug
MAX_PER_SECOND = settings.CLIENT_MAX_PER_SECOND
MAX_PER_MINUTE = settings.CLIENT_MAX_PER_MINUTE


class RateLimitTransport(httpx.AsyncHTTPTransport):

    def __init__(
        self,
        max_per_second: int,
        max_per_minute: int,
        **kwargs
    ) -> None:
        self.loop = asyncio.get_running_loop()
        self.max_per_second = max_per_second
        self.max_per_minute = max_per_minute
        self.second = []
        self.minute = []
        super().__init__(**kwargs)

    async def notify_period(
        self,
        history: list[float],
        period: float,
        max_per_period: int
    ) -> float:
        while True:
            now = self.loop.time()
            while history and now - history[0] > period:
                history.pop(0)
            if len(history) < max_per_period:
                break
            await asyncio.sleep(max(0.0, period - (now - history[0])))
        return now

    async def notify(self):
        if not self.max_per_second and not self.max_per_minute:
            return
        if self.max_per_second:
            now = await self.notify_period(
                history=self.second,
                period=1.0,
                max_per_period=self.max_per_second
            )
        if self.max_per_minute:
            now = await self.notify_period(
                history=self.minute,
                period=60.0,
                max_per_period=self.max_per_minute
            )
        self.second.append(now)
        self.minute.append(now)

    async def handle_async_request(
        self,
        request: httpx.Request
    ) -> httpx.Response:
        await self.notify()
        return await super().handle_async_request(request)

    async def __aenter__(self) -> Self:
        await self.notify()
        return await super().__aenter__()


class BybitClient:

    __instance: Self = None

    HOST = 'api-testnet.bybit.com'
    TEST_HOST = 'api-testnet.bybit.com'

    START_TIME_COLUMN = 'start_time'
    OPEN_PRICE_COLUMN = 'open_price'
    HIGH_PRICE_COLUMN = 'high_price'
    LOW_PRICE_COLUMN = 'low_price'
    CLOSE_PRICE_COLUMN = 'close_price'
    VOLUME_COLUMN = 'volume'
    TURNOVER_COLUMN = 'turnover'
    CANDLE_COLUMNS = [START_TIME_COLUMN, OPEN_PRICE_COLUMN, HIGH_PRICE_COLUMN,
                      LOW_PRICE_COLUMN, VOLUME_COLUMN, TURNOVER_COLUMN]

    @classmethod
    def rsi(cls, data: DataFrame) -> float | None:
        if data.empty:
            return
        result = pandas_ta.rsi(data[cls.CLOSE_PRICE_COLUMN])
        return float(result.iloc[-1])

    @classmethod
    def atr(cls, data: DataFrame) -> float | None:
        if data.empty:
            return
        result = pandas_ta.atr(
            high=data[cls.HIGH_PRICE_COLUMN],
            low=data[cls.LOW_PRICE_COLUMN],
            close=data[cls.CLOSE_PRICE_COLUMN]
        )
        return float(result.iloc[-1])

    def __new__(cls) -> Self:
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, debug: bool = DEBUG) -> None:
        self.host = type(self).TEST_HOST if debug else type(self).HOST
        self.client = httpx.AsyncClient(
            transport=RateLimitTransport(
                max_per_second=MAX_PER_SECOND,
                max_per_minute=MAX_PER_MINUTE
            )
        )

    async def close(self) -> None:
        await self.client.aclose()

    async def get(
        self,
        endpoint: str,
        params: dict[str, Any]
    ) -> dict[str, Any]:
        response = await self.client.get(
            url=f'https://{self.host}/{endpoint}',
            params=params
        )
        if response.status_code == httpx.codes.OK:
            return response.json()

    async def get_candles(
        self,
        symbol: str,
        interval: str,
        limit: int = 200
    ) -> DataFrame:
        json = await self.get(
            endpoint='v5/market/kline',
            params={
                'category': 'linear',
                'symbol': symbol,
                'interval': interval,
                'limit': limit,
            }
        )
        if not json:
            return DataFrame(columns=self.CANDLE_COLUMNS)
        candles = [
            {
                self.START_TIME_COLUMN: float(candle[0]) / 1000.0,
                self.OPEN_PRICE_COLUMN: float(candle[1]),
                self.HIGH_PRICE_COLUMN: float(candle[2]),
                self.LOW_PRICE_COLUMN: float(candle[3]),
                self.CLOSE_PRICE_COLUMN: float(candle[4]),
                self.VOLUME_COLUMN: float(candle[5]),
                self.TURNOVER_COLUMN: float(candle[6]),
            }
            for candle in reversed(json['result']['list'])
        ]
        return DataFrame(candles)

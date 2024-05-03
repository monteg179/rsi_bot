import asyncio
import enum
from typing import (
    Any,
    Self,
)

import httpx
from pandas import (
    DataFrame,
)

from rsi_bot.exceptions import (
    BybitClientConnectionError,
    BybitClientError,
    BybitClientResponseError,
)
from rsi_bot import settings
from rsi_bot import ta

DEBUG = settings.Enviroment().debug
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


class KLineInterval(enum.Enum):
    minute = '1'
    hour = '60'
    day = 'D'
    week = 'W'
    month = 'M'
    minute_x3 = '3'
    minute_x5 = '5'
    minute_x15 = '15'
    minute_x30 = '30'
    hour_x2 = '120'
    hour_x4 = '240'
    hour_x6 = '360'
    hour_x12 = '720'


class BybitClient:

    __instance: Self = None

    HOST = 'api.bybit.com'
    TEST_HOST = 'api-testnet.bybit.com'

    KLINE_ENDPOINT = 'v5/market/kline'

    KLINE_MIN_LIMIT = 1
    KLINE_MAX_LIMIT = 1000

    START_TIME_COLUMN = 'start_time'
    OPEN_PRICE_COLUMN = 'open_price'
    HIGH_PRICE_COLUMN = 'high_price'
    LOW_PRICE_COLUMN = 'low_price'
    CLOSE_PRICE_COLUMN = 'close_price'
    VOLUME_COLUMN = 'volume'
    TURNOVER_COLUMN = 'turnover'

    @classmethod
    def rsi(cls, data: DataFrame) -> float:
        indicator = ta.rsi(data[cls.CLOSE_PRICE_COLUMN])
        return float(indicator.iloc[-1])

    @classmethod
    def volatility(cls, data: DataFrame) -> float:
        indicator = ta.volatility(
            high=data[cls.HIGH_PRICE_COLUMN],
            low=data[cls.LOW_PRICE_COLUMN],
            close=data[cls.CLOSE_PRICE_COLUMN]
        )
        return float(indicator.iloc[-1])

    @classmethod
    def flats(
        cls,
        data: DataFrame,
        max_difference: float,
        min_length: int,
        va: float
    ) -> list[dict[str, float]]:
        flats = ta.flats(
            close=data[cls.CLOSE_PRICE_COLUMN],
            max_difference=max_difference,
            min_length=min_length
        )
        result = []
        if flats:
            for flat in flats:
                frame = data.iloc[flat[0]:flat[1]]
                result.append(ta.poc_val_vah(
                    high=frame[cls.HIGH_PRICE_COLUMN],
                    low=frame[cls.LOW_PRICE_COLUMN],
                    volume=frame[cls.VOLUME_COLUMN],
                    va=va
                ))
        return result

    @classmethod
    def trend(cls, data: DataFrame, length: int = 14) -> int:
        return ta.trend(
            high=data[cls.HIGH_PRICE_COLUMN][:-4],
            low=data[cls.LOW_PRICE_COLUMN][:-4],
            close=data[cls.CLOSE_PRICE_COLUMN][:-4],
            length=length
        )

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
        params: dict[str, Any],
        countdown: int = 10,
        sleep: float = 30.0
    ) -> dict[str, Any]:
        while countdown > 0:
            try:
                response = await self.client.get(
                    url=f'https://{self.host}/{endpoint}',
                    params=params
                )
                status_code = response.status_code
                if not status_code == httpx.codes.OK:
                    raise httpx.HTTPStatusError(
                        message=f'status_code: {status_code}',
                        request=response.request,
                        response=response
                    )
            except Exception:
                countdown -= 1
                await asyncio.sleep(sleep)
            else:
                return response.json()
        else:
            raise BybitClientConnectionError()

    async def get_candles(
        self,
        symbol: str,
        interval: KLineInterval,
        limit: int
    ) -> DataFrame:
        if limit < self.KLINE_MIN_LIMIT or limit > self.KLINE_MAX_LIMIT:
            raise BybitClientError(f'limit invalid value: {limit}')
        json = await self.get(
            endpoint=self.KLINE_ENDPOINT,
            params={
                'category': 'linear',
                'symbol': symbol,
                'interval': interval.value,
                'limit': limit,
            }
        )
        try:
            json_candles = json['result']['list']
            if not len(json_candles) == limit:
                raise BybitClientResponseError()
            candles = [
                {
                    type(self).START_TIME_COLUMN: float(candle[0]) / 1000.0,
                    type(self).OPEN_PRICE_COLUMN: float(candle[1]),
                    type(self).HIGH_PRICE_COLUMN: float(candle[2]),
                    type(self).LOW_PRICE_COLUMN: float(candle[3]),
                    type(self).CLOSE_PRICE_COLUMN: float(candle[4]),
                    type(self).VOLUME_COLUMN: float(candle[5]),
                    type(self).TURNOVER_COLUMN: float(candle[6]),
                }
                for candle in reversed(json_candles)
            ]
        except Exception as error:
            raise BybitClientResponseError() from error
        else:
            return DataFrame(candles)

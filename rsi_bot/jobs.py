from typing import (
    Coroutine,
    Type,
)

from telegram.ext import (
    JobQueue,
)

from rsi_bot.bybit import (
    BybitClient,
    KLineInterval,
)
from rsi_bot.exceptions import (
    BotJobsShellError,
)
from rsi_bot import settings

RSI_INTERVAL = settings.BOT_RSI_JOB_INTERVAL
VOLATILITY_INTERVAL = settings.BOT_VOLATILITY_JOB_INTERVAL
FLATS_INTERVAL = settings.BOT_FLATS_JOB_INTERVAL
TREND_INTERVAL = settings.BOT_TREND_JOB_INTERVAL


class BotJobHelper:

    prefix: str
    interval: float

    @classmethod
    def get_usage_message(cls) -> str:
        raise NotImplementedError()

    @classmethod
    def get_prefix(cls) -> str:
        return cls.prefix

    @classmethod
    def get_interval(cls) -> float:
        return cls.interval

    def __init__(self, user_id: int) -> None:
        self.__user_id = user_id

    def get_name(self) -> str:
        raise NotImplementedError()

    def get_title(self) -> str:
        raise NotImplementedError()

    async def execute(self) -> str | None:
        raise NotImplementedError()

    @property
    def user_id(self) -> int:
        return self.__user_id

    @property
    def name(self) -> str:
        return self.get_name()

    @property
    def title(self) -> str:
        return self.get_title()


class RsiJob(BotJobHelper):

    prefix = 'rsi'
    interval = RSI_INTERVAL
    timeframes: dict[str, tuple[int, KLineInterval]] = {
        '30': (30, KLineInterval.minute),
        '240': (240, KLineInterval.minute),
    }

    @classmethod
    def get_usage_message(cls) -> str:
        timeframes = ' '.join(
            str(timeframe) for timeframe in cls.timeframes.keys()
        )
        return (f'{cls.get_prefix()} <coin> <timeframe> <setpoint>\n'
                f'coin: string\ntimeframe: {timeframes}\nsetpoint: float')

    def __init__(
        self,
        user_id: int,
        coin: str,
        timeframe: str,
        setpoint: str
    ) -> None:
        super().__init__(user_id)
        self.__coin = coin
        if timeframe not in self.timeframes.keys():
            raise ValueError(f'timeframe invalid value: {timeframe}')
        self.__timeframe = timeframe
        self.__setpoint = float(setpoint)

    def get_name(self) -> str:
        prefix = self.get_prefix().lower()
        return (f'{self.user_id}-'
                f'{prefix}-'
                f'{self.__coin}-'
                f'{self.__timeframe}-'
                f'{self.__setpoint}')

    def get_title(self) -> str:
        prefix = self.get_prefix().upper()
        return (f'{prefix}'
                f'[{self.__coin}, '
                f'{self.__timeframe}, '
                f'{self.__setpoint}]')

    async def execute(self) -> str | None:
        limit, interval = self.timeframes[self.__timeframe]
        data = await BybitClient().get_candles(
            symbol=self.__coin,
            interval=interval,
            limit=limit
        )
        value = BybitClient.rsi(data)
        if value < self.__setpoint * 0.15 or value > self.__setpoint * 0.85:
            return f'{self.get_title()}:\n{value:.2f}'


class VolatilityJob(BotJobHelper):

    prefix = 'volatility'
    interval = VOLATILITY_INTERVAL
    timeframes: dict[str, tuple[int, KLineInterval]] = {
        '30': (30, KLineInterval.minute),
        '240': (240, KLineInterval.minute),
    }

    @classmethod
    def get_usage_message(cls) -> str:
        timeframes = ' '.join(
            str(timeframe) for timeframe in cls.timeframes.keys()
        )
        return (f'{cls.get_prefix()} <coin> <timeframe> <setpoint>\n'
                f'coint: string\ntimeframe: {timeframes}\nsetpoint: float')

    def __init__(
        self,
        user_id: int,
        coin: str,
        timeframe: str,
        setpoint: str
    ) -> None:
        super().__init__(user_id)
        self.__coin = coin
        if timeframe not in self.timeframes.keys():
            raise ValueError(f'timeframe invalid value: {timeframe}')
        self.__timeframe = timeframe
        self.__setpoint = float(setpoint)

    def get_name(self) -> str:
        prefix = self.get_prefix().lower()
        return (f'{self.user_id}-'
                f'{prefix}-'
                f'{self.__coin}-'
                f'{self.__timeframe}-'
                f'{self.__setpoint}')

    def get_title(self) -> str:
        prefix = self.get_prefix().upper()
        return (f'{prefix}['
                f'{self.__coin}, '
                f'{self.__timeframe},'
                f'{self.__setpoint}]')

    async def execute(self) -> str | None:
        limit, interval = self.timeframes[self.__timeframe]
        data = await BybitClient().get_candles(
            symbol=self.__coin,
            interval=interval,
            limit=limit,
        )
        value = BybitClient.volatility(data)
        if value < self.__setpoint * 0.15 or value > self.__setpoint * 0.85:
            return f'{self.get_title()}:\n{value:.2f}'


class FlatsJob(BotJobHelper):

    prefix = 'flats'
    interval = FLATS_INTERVAL
    timeframes: dict[str, tuple[int, KLineInterval]] = {
        '30': (30, KLineInterval.minute),
        '60': (60, KLineInterval.minute),
        '240': (240, KLineInterval.minute),
        '1440': (480, KLineInterval.minute_x3)
    }

    @classmethod
    def get_usage_message(cls) -> str:
        timeframes = ' '.join(
            str(timeframe) for timeframe in cls.timeframes.keys()
        )
        return (f'{cls.get_prefix()} <coin> <timeframe> <max_difference> '
                f'<min_length> <va>\ncoin: string\ntimeframes: {timeframes}\n'
                f'max_difference: float\nmin_length: integer\nva: float')

    def __init__(
        self,
        user_id: int,
        coin: str,
        timeframe: str,
        max_difference: str,
        min_length: str,
        va: str
    ) -> None:
        super().__init__(user_id)
        self.__coin = coin
        if timeframe not in self.timeframes.keys():
            raise ValueError(f'timeframe invalid value: {timeframe}')
        self.__timeframe = timeframe
        self.__max_difference = float(max_difference)
        self.__min_length = int(min_length)
        self.__va = float(va)

    def get_name(self) -> str:
        prefix = self.get_prefix().lower()
        return (f'{self.user_id}-'
                f'{prefix}-'
                f'{self.__coin}-'
                f'{self.__timeframe}-'
                f'{self.__max_difference}-'
                f'{self.__min_length}-'
                f'{self.__va}')

    def get_title(self) -> str:
        prefix = self.get_prefix().upper()
        return (f'{prefix}['
                f'{self.__coin}, '
                f'{self.__timeframe}, '
                f'{self.__max_difference}, '
                f'{self.__min_length}, '
                f'{self.__va}]')

    async def execute(self) -> str | None:
        limit, interval = self.timeframes[self.__timeframe]
        data = await BybitClient().get_candles(
            symbol=self.__coin,
            interval=interval,
            limit=limit
        )
        flats = BybitClient.flats(
            data=data,
            max_difference=self.__max_difference,
            min_length=self.__min_length,
            va=self.__va
        )
        if flats:
            result = [
                f'val={flat["val"]:.2f}, poc={flat["poc"]}, vah={flat["vah"]}'
                for flat in flats
            ]
            return f'{self.title}:\n' + '\n'.join(result)


class TrendJob(BotJobHelper):

    prefix = 'trend'
    interval = TREND_INTERVAL
    timeframes: dict[str, tuple[int, KLineInterval]] = {
        '30': (30, KLineInterval.minute),
        '60': (60, KLineInterval.minute),
        '240': (240, KLineInterval.minute),
        '1440': (480, KLineInterval.minute_x3)
    }

    @classmethod
    def get_usage_message(cls) -> str:
        timeframes = ' '.join(
            str(timeframe) for timeframe in cls.timeframes.keys()
        )
        return (f'{cls.get_prefix()} <coin> <timeframe> <setpoint>\n'
                f'coint: string\ntimeframe: {timeframes}\n')

    def __init__(self, user_id: int, coin: str, timeframe: str) -> None:
        super().__init__(user_id)
        self.__coin = coin
        if timeframe not in self.timeframes.keys():
            raise ValueError(f'timeframe invalid value: {timeframe}')
        self.__timeframe = timeframe

    def get_name(self) -> str:
        prefix = self.get_prefix().lower()
        return (f'{self.user_id}-'
                f'{prefix}-'
                f'{self.__coin}-'
                f'{self.__timeframe}')

    def get_title(self) -> str:
        prefix = self.get_prefix().upper()
        return (f'{prefix}['
                f'{self.__coin}, '
                f'{self.__timeframe}]')

    async def execute(self) -> str | None:
        limit, interval = self.timeframes[self.__timeframe]
        data = await BybitClient().get_candles(
            symbol=self.__coin,
            interval=interval,
            limit=limit
        )
        result = BybitClient.trend(data)
        if result > 0:
            return f'{self.get_title()}:\ndowntrend to uptrend'
        if result < 0:
            return f'{self.get_title()}:\nuptrend to downtrend'


class BotJobsShell:

    HELPERS: list[Type[BotJobHelper]] = [
        RsiJob,
        VolatilityJob,
        FlatsJob,
        TrendJob,
    ]

    @staticmethod
    def remove_jobs_by_name(queue: JobQueue, name: str) -> str | None:
        jobs = queue.get_jobs_by_name(name)
        if jobs:
            for job in jobs:
                job.schedule_removal()
            return '\n'.join(
                [
                    f'Remove {job.data.title} job'
                    for job in jobs
                    if isinstance(job.data, BotJobHelper)
                ]
            )

    @staticmethod
    def remove_all_jobs(queue: JobQueue) -> None:
        for job in queue.jobs():
            job.schedule_removal()

    @classmethod
    def get_helper_class(cls, prefix: str) -> Type[BotJobHelper]:
        for helper_class in cls.HELPERS:
            if prefix.lower() == helper_class.get_prefix().lower():
                return helper_class
        raise ValueError('prefix invalid value')

    @classmethod
    def add_job(
        cls,
        args: list[str],
        user_id: int,
        chat_id: int,
        queue: JobQueue,
        callback: Coroutine
    ) -> str:
        try:
            helper_class = cls.get_helper_class(args.pop(0))
        except Exception as error:
            prefixes = [helper.get_prefix() for helper in cls.HELPERS]
            raise BotJobsShellError(
                message=f'<job_type>\njob_type: {",".join(prefixes)}'
            ) from error
        else:
            try:
                helper = helper_class(user_id, *args)
            except Exception as error:
                raise BotJobsShellError(
                    message=helper_class.get_usage_message()
                ) from error
            else:
                removed = cls.remove_jobs_by_name(queue, helper.name)
                queue.run_repeating(
                    callback=callback,
                    interval=helper_class.get_interval(),
                    name=helper.name,
                    chat_id=chat_id,
                    user_id=user_id,
                    data=helper
                )
                if removed:
                    return f'{removed}\nAdd {helper.title} job'
                return f'Add {helper.title} job'

    @classmethod
    def remove_job(
        cls,
        args: list[str],
        user_id: int,
        queue: JobQueue
    ) -> str:
        try:
            helper_class = cls.get_helper_class(args.pop(0))
        except Exception as error:
            prefixes = [helper.get_prefix() for helper in cls.HELPERS]
            raise BotJobsShellError(
                message=f'<job_type>\njob_type: {",".join(prefixes)}'
            ) from error
        else:
            try:
                helper = helper_class(user_id, *args)
            except Exception as error:
                raise BotJobsShellError(
                    message=helper_class.get_usage_message()
                ) from error
            else:
                return cls.remove_jobs_by_name(queue, helper.name)

    @classmethod
    def jobs_list(cls, args: list[str], user_id: int, queue: JobQueue) -> str:
        try:
            if args:
                helper_class = cls.get_helper_class(args[0])
                jobs = [
                    job.data for job in queue.jobs()
                    if (job.user_id == user_id and
                        isinstance(job.data, helper_class))
                ]
            else:
                jobs = [
                    job.data for job in queue.jobs()
                    if (job.user_id == user_id and
                        isinstance(job.data, BotJobHelper))
                ]
        except Exception as error:
            prefixes = [helper.get_prefix() for helper in cls.HELPERS]
            raise BotJobsShellError(
                message=f'<job_type>\njob_type: {",".join(prefixes)}'
            ) from error
        else:
            return '\n'.join([job.title for job in jobs])
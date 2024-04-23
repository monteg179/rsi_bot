from typing import (
    Self,
)

from dotenv import (
    load_dotenv,
)
import logging
import os


LOG_LEVEL = logging.INFO

BOT_RSI_JOB_INTERVAL = 1800.0
BOT_ATR_JOB_INTERVAL = 1800.0
BOT_TIMEFRAMES = [30, 240]

CLIENT_MAX_PER_SECOND = 3
CLIENT_MAX_PER_MINUTE = 100


class DotEnv:

    DEBUG = 'DEBUG'
    TELEGRAM_TOKEN = 'TELEGRAM_TOKEN'
    BYBIT_API_KEY = 'BYBIT_API_KEY'
    BYBIT_API_SECRET = 'BYBIT_API_SECRET'

    __instance: Self = None

    def __new__(cls) -> Self:
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self) -> None:
        load_dotenv()
        self.__debug = os.getenv('DEBUG', 'false').lower() == 'true'
        self.__telegram_token = os.getenv(
            key=type(self).TELEGRAM_TOKEN
        )
        self.__bybit_api_key = os.getenv(
            key=type(self).BYBIT_API_KEY
        )
        self.__bybit_api_secret = os.getenv(
            key=type(self).BYBIT_API_KEY
        )

    @property
    def debug(self) -> bool:
        return self.__debug

    @property
    def telegram_token(self) -> str:
        return self.__telegram_token

    @property
    def bybit_api_key(self) -> str:
        return self.__bybit_api_key

    @property
    def bybit_api_secret(self) -> str:
        return self.__bybit_api_secret

import logging
import os
from typing import (
    Self,
)

from dotenv import (
    load_dotenv,
)

LOG_LEVEL = logging.INFO

BOT_RSI_JOB_INTERVAL = 1800.0
BOT_VOLATILITY_JOB_INTERVAL = 1800.0
BOT_FLATS_JOB_INTERVAL = 1800.0
BOT_TREND_JOB_INTERVAL = 1800.0

CLIENT_MAX_PER_SECOND = 3
CLIENT_MAX_PER_MINUTE = 100


class Enviroment:

    DEBUG = 'DEBUG'
    TELEGRAM_TOKEN = 'TELEGRAM_TOKEN'
    WEBHOOK_PORT = 'WEBHOOK_PORT'
    WEBHOOK_URL = 'WEBHOOK_URL'
    WEBHOOK_SECRET = 'WEBHOOK_SECRET'
    WEBHOOK_PATH = 'WEBHOOK_PATH'
    WEBHOOK_CERT = 'WEBHOOK_CERT'
    WEBHOOK_KEY = 'WEBHOOK_KEY'
    BYBIT_API_KEY = 'BYBIT_API_KEY'
    BYBIT_API_SECRET = 'BYBIT_API_SECRET'

    __instance: Self = None

    @classmethod
    def get_instance(cls) -> Self:
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __new__(cls) -> Self:
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self) -> None:
        load_dotenv()
        self.__debug = os.getenv(type(self).DEBUG, 'false').lower() == 'true'
        self.__telegram_token = os.getenv(type(self).TELEGRAM_TOKEN)
        self.__webhook_port = int(os.getenv(type(self).WEBHOOK_PORT, 0))
        self.__webhook_url = os.getenv(type(self).WEBHOOK_URL)
        self.__webhook_secret = os.getenv(type(self).WEBHOOK_SECRET)
        self.__webhook_path = os.getenv(type(self).WEBHOOK_PATH, '')
        self.__webhook_cert = os.getenv(type(self).WEBHOOK_CERT)
        self.__webhook_key = os.getenv(type(self).WEBHOOK_KEY)
        self.__bybit_api_key = os.getenv(type(self).BYBIT_API_KEY)
        self.__bybit_api_secret = os.getenv(type(self).BYBIT_API_SECRET)

    @property
    def debug(self) -> bool:
        return self.__debug

    @property
    def telegram_token(self) -> str:
        return self.__telegram_token

    @property
    def webhook_url(self) -> str | None:
        return self.__webhook_url

    @property
    def webhook_port(self) -> int | None:
        return self.__webhook_port

    @property
    def webhook_secret(self) -> str | None:
        return self.__webhook_secret

    @property
    def webhook_path(self) -> str | None:
        return self.__webhook_path

    @property
    def webhook_cert(self) -> str | None:
        return self.__webhook_cert

    @property
    def webhook_key(self) -> str | None:
        return self.__webhook_key

    @property
    def bybit_api_key(self) -> str | None:
        return self.__bybit_api_key

    @property
    def bybit_api_secret(self) -> str | None:
        return self.__bybit_api_secret

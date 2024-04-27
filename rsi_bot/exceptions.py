from typing import (
    Optional,
)


class BybitClientError(Exception):
    pass


class BybitClientConnectionError(BybitClientError):
    pass


class BybitClientResponseError(BybitClientError):

    def __init__(self, status_code: Optional[int]) -> None:
        self.__status_code = status_code

    def __str__(self) -> str:
        if self.__status_code is None:
            return 'invalid response'
        return f'status code: {self.__status_code}'


class BotJobsShellError(Exception):

    def __init__(self, message: str) -> None:
        self.__message = message

    def __str__(self) -> str:
        return self.__message

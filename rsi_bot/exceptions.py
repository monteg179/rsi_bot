class BybitClientError(Exception):
    pass


class BybitClientConnectionError(BybitClientError):

    MESSAGE = 'connection error'

    def __str__(self) -> str:
        return type(self).MESSAGE


class BybitClientResponseError(BybitClientError):

    MESSAGE = 'incorrect response format'

    def __str__(self) -> str:
        return type(self).MESSAGE


class BotJobsShellError(Exception):

    def __init__(self, message: str) -> None:
        self.__message = message

    def __str__(self) -> str:
        return self.__message

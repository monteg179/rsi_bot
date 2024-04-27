import logging

from rsi_bot import (
    build_bot_application,
    run_bot_application,
)
from rsi_bot import settings

LOG_LEVEL = settings.LOG_LEVEL


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=LOG_LEVEL
)
logging.getLogger('httpx').setLevel(logging.INFO)
logger = logging.getLogger(__name__)

application = build_bot_application()


def main():
    run_bot_application(application)


if __name__ == '__main__':
    main()

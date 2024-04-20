import logging

from rsi_bot.bot import (
    build_bot_application,
    run_bot_application,
)
from rsi_bot.settings import (
    LOG_LEVEL
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=LOG_LEVEL
)
logging.getLogger('httpx').setLevel(logging.INFO)
logger = logging.getLogger(__name__)


def main():
    application = build_bot_application()
    run_bot_application(application)


if __name__ == '__main__':
    main()

import logging
import os

from dotenv import (
    load_dotenv,
)
from telegram import (
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    JobQueue,
)

from bybit import (
    Bybit,
)

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger('httpx').setLevel(logging.INFO)
logger = logging.getLogger(__name__)


def remove_job(name: str, queue: JobQueue) -> None:
    jobs = queue.get_jobs_by_name(name)
    for job in jobs:
        job.schedule_removal()


async def rsi(context: ContextTypes.DEFAULT_TYPE) -> None:
    await Bybit.get_kline('BTCUSD', '30', 10)


async def volatility(context: ContextTypes.DEFAULT_TYPE) -> None:
    await Bybit.get_historical_volatility('option', 'BTC', 30)


async def poc(context: ContextTypes.DEFAULT_TYPE) -> None:
    await Bybit.get_kline('BTCUSD', '30', 10)


async def rsi_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat_id = update.effective_message.chat_id
    job_name = str(chat_id)
    remove_job(job_name, context.job_queue)
    context.job_queue.run_repeating(
        callback=rsi,
        first=30.0,
        interval=30.0,
        chat_id=chat_id,
        name=job_name
    )


async def volatility_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat_id = update.effective_message.chat_id
    job_name = str(chat_id)
    remove_job(job_name, context.job_queue)
    context.job_queue.run_repeating(
        callback=volatility,
        first=30.0,
        interval=30.0,
        chat_id=chat_id,
        name=job_name
    )


async def poc_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat_id = update.effective_message.chat_id
    job_name = str(chat_id)
    remove_job(job_name, context.job_queue)
    context.job_queue.run_repeating(
        callback=poc,
        first=30.0,
        interval=30.0,
        chat_id=chat_id,
        name=job_name
    )


def main() -> None:
    token = os.getenv('TELEGRAM_TOKEN')
    app = Application.builder().token(token).build()
    app.add_handler(
        CommandHandler('rsi', rsi_handler)
    )
    app.add_handler(
        CommandHandler('volatility', volatility_handler)
    )
    app.add_handler(
        CommandHandler('poc', poc_handler)
    )
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

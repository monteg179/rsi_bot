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


def remove_all_jobs(queue: JobQueue) -> None:
    for job in queue.jobs():
        job.schedule_removal()


async def rsi_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    data = context.job.data
    json = await Bybit.get_kline(data['coin'], data['timeframe'])
    if json:
        rsi = Bybit.get_kline_rsi(json, data['rsi_length'])
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=f'rsi: {rsi:.2f}'
        )


async def volatility_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await Bybit.get_historical_volatility('option', 'BTC', 30)
    if data:
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text='volatility: '
        )


async def poc_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await Bybit.get_kline('BTCUSD', '30', 10)
    if data:
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text='poc: '
        )


async def rsi_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    try:
        coin = context.args[0]
        timeframe = context.args[1]
        rsi_length = int(context.args[2])
    except Exception:
        await context.bot.send_message(
            chat_id=chat_id,
            text='Usage: /rsi <coin> <timeframe> <rsi length>'
        )
    else:
        job_name = str(chat_id)
        remove_job(job_name, context.job_queue)
        context.job_queue.run_repeating(
            callback=rsi_job,
            interval=30.0,
            chat_id=chat_id,
            user_id=user_id,
            data={
                'coin': coin,
                'timeframe': timeframe,
                'rsi_length': rsi_length,
            },
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
        callback=volatility_job,
        interval=60.0,
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
        callback=poc_job,
        interval=60.0,
        chat_id=chat_id,
        name=job_name
    )


async def stop_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    remove_all_jobs(context.job_queue)


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
    app.add_handler(
        CommandHandler('stop', stop_handler)
    )
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

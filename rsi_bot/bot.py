from telegram import (
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    JobQueue,
)

from rsi_bot.bybit import (
    BybitClient,
)
from rsi_bot import settings


TELEGRAM_TOKEN = settings.Secrets().telegram_token
RSI_JOB_INTERVAL = settings.BOT_RSI_JOB_INTERVAL
ATR_JOB_INTERVAL = settings.BOT_ATR_JOB_INTERVAL


def remove_job(name: str, queue: JobQueue) -> None:
    jobs = queue.get_jobs_by_name(name)
    for job in jobs:
        job.schedule_removal()


def remove_all_jobs(queue: JobQueue) -> None:
    for job in queue.jobs():
        job.schedule_removal()


async def rsi_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await BybitClient().get_candles(
        symbol=context.job.data['coin'],
        interval=context.job.data['timeframe']
    )
    value = BybitClient.rsi(data)
    if value < context.job.data['min'] or value > context.job.data['max']:
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=f'rsi: {value:.2f}'
        )


async def atr_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await BybitClient().get_candles(
        symbol=context.job.data['coin'],
        interval=context.job.data['timeframe']
    )
    value = BybitClient.atr(data)
    if value < context.job.data['min'] or value > context.job.data['max']:
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=f'atr: {value:.2f}'
        )


async def poc_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=f'poc {context.job.data}'
    )


async def trend_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=f'trend {context.job.data}'
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
        minimum = float(context.args[2])
        maximum = float(context.args[3])
    except Exception:
        await context.bot.send_message(
            chat_id=chat_id,
            text='Usage: /rsi <coin> <timeframe> <min> <max>'
        )
    else:
        job_name = str(chat_id)
        remove_job(job_name, context.job_queue)
        context.job_queue.run_repeating(
            callback=rsi_job,
            interval=RSI_JOB_INTERVAL,
            first=1.0,
            name=job_name,
            chat_id=chat_id,
            user_id=user_id,
            data={
                'coin': coin,
                'timeframe': timeframe,
                'min': minimum,
                'max': maximum,
            }
        )


async def atr_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    try:
        coin = context.args[0]
        timeframe = context.args[1]
        minimum = float(context.args[2])
        maximum = float(context.args[3])
    except Exception:
        await context.bot.send_message(
            chat_id=chat_id,
            text='Usage: /atr <coin> <timeframe> <min> <max>'
        )
    else:
        job_name = str(chat_id)
        remove_job(job_name, context.job_queue)
        context.job_queue.run_repeating(
            callback=atr_job,
            interval=ATR_JOB_INTERVAL,
            first=1.0,
            name=job_name,
            chat_id=chat_id,
            user_id=user_id,
            data={
                'coin': coin,
                'timeframe': timeframe,
                'min': minimum,
                'max': maximum,
            }
        )


async def poc_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat_id = update.effective_message.chat_id
    user_id = update.effective_user.id
    try:
        data = context.args
    except Exception:
        await context.bot.send_message(
            chat_id=chat_id,
            text='Usage: /poc'
        )
    else:
        job_name = str(chat_id)
        remove_job(job_name, context.job_queue)
        context.job_queue.run_repeating(
            callback=poc_job,
            interval=60.0,
            name=job_name,
            chat_id=chat_id,
            user_id=user_id,
            data={
                'data': data,
            }
        )


async def trend_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    try:
        data = context.args
    except Exception:
        await context.bot.send_message(
            chat_id=chat_id,
            text='Usage: /trend'
        )
    else:
        job_name = str(chat_id)
        remove_job(job_name, context.job_queue)
        context.job_queue.run_repeating(
            callback=rsi_job,
            interval=30.0,
            name=job_name,
            chat_id=chat_id,
            user_id=user_id,
            data={
                'data': data,
            }
        )


async def stop_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    remove_all_jobs(context.job_queue)


def build_bot_application() -> Application:
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(
        CommandHandler('rsi', rsi_handler)
    )
    app.add_handler(
        CommandHandler('atr', atr_handler)
    )
    app.add_handler(
        CommandHandler('poc', poc_handler)
    )
    app.add_handler(
        CommandHandler('trend', trend_handler)
    )
    app.add_handler(
        CommandHandler('stop', stop_handler)
    )
    return app


def run_bot_application(app: Application) -> None:
    app.run_polling(allowed_updates=Update.ALL_TYPES)

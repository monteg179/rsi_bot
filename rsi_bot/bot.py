from telegram import (
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    Job,
    JobQueue,
)

from rsi_bot.bybit import (
    BybitClient,
)
from rsi_bot import settings


TELEGRAM_TOKEN = settings.DotEnv().telegram_token
RSI_JOB_INTERVAL = settings.BOT_RSI_JOB_INTERVAL
ATR_JOB_INTERVAL = settings.BOT_ATR_JOB_INTERVAL
POC_JOB_INTERVAL = settings.BOT_POC_JOB_INTERVAL
TIMEFRAMES = settings.BOT_TIMEFRAMES

RSI_JOB = 'rsi'
ATR_JOB = 'atr'
POC_JOB = 'poc'
TREND_JOB = 'trend'
ALL_JOBS = 'all'


def rsi_job_title(job: Job) -> str | None:
    if not job.data['type'] == RSI_JOB:
        return
    coin = job.data['coin']
    timeframe = job.data['timeframe']
    setpoint = job.data['setpoint']
    return f'RSI[{coin}, {timeframe}, {setpoint}]'


def atr_job_title(job: Job) -> str | None:
    if not job.data['type'] == ATR_JOB:
        return
    coin = job.data['coin']
    timeframe = job.data['timeframe']
    setpoint = job.data['setpoint']
    return f'ATR[{coin}, {timeframe}, {setpoint}]'


def poc_job_title(job: Job) -> str | None:
    if not job.data['type'] == POC_JOB:
        return
    coin = job.data['coin']
    timeframe = job.data['timeframe']
    return f'POC[{coin}, {timeframe}]'


def trend_job_title(job: Job) -> str | None:
    pass


def job_title(job: Job) -> str | None:
    job_type = job.data['type']
    if job_type == RSI_JOB:
        return rsi_job_title(job)
    elif job_type == ATR_JOB:
        return atr_job_title(job)
    elif job_type == POC_JOB:
        return poc_job_title(job)
    elif job_type == TREND_JOB:
        return trend_job_title(job)


async def rsi_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    coin = context.job.data['coin']
    timeframe = context.job.data['timeframe']
    setpoint = context.job.data['setpoint']
    data = await BybitClient().get_candles(
        symbol=coin,
        interval=timeframe
    )
    value = BybitClient.rsi(data)
    if value < setpoint * 0.15 or value > setpoint * 0.85:
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=f'{rsi_job_title(context.job)}:\n{value:.2f}'
        )


async def atr_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    coin = context.job.data['coin']
    timeframe = context.job.data['timeframe']
    setpoint = context.job.data['setpoint']
    data = await BybitClient().get_candles(coin, timeframe)
    value = BybitClient.atr(data)
    if value < setpoint * 0.15 or value > setpoint * 0.85:
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=f'{atr_job_title(context.job)}:\n{value:.2f}'
        )


async def poc_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    coin = context.job.data['coin']
    timeframe = context.job.data['timeframe']
    data = await BybitClient().get_candles(coin, timeframe)
    value = BybitClient.poc(data)
    val = value.get('val')
    poc = value.get('poc')
    vah = value.get('vah')
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=f'{poc_job_title(context.job)}:\n{vah:.2f}\n{poc:.2f}\n{val:.2f}'
    )


async def trend_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=f'trend {context.job.data}'
    )


def rsi_job_name(
    user_id: int,
    coin: str,
    timeframe: int,
    setpoint: int
) -> str:
    return f'{user_id}-{RSI_JOB}-{coin}-{timeframe}-{setpoint}'


def atr_job_name(
    user_id: int,
    coin: str,
    timeframe: int,
    setpoint: int
) -> str:
    return f'{user_id}-{ATR_JOB}-{coin}-{timeframe}-{setpoint}'


def poc_job_name(user_id: int, coin: str, timeframe: int) -> str:
    return f'{user_id}-{POC_JOB}-{coin}-{timeframe}'


def trend_job_name(user_id: int) -> str:
    return f'{user_id}-{TREND_JOB}-'


async def add_rsi_job(
    user_id: int,
    chat_id: int,
    context: ContextTypes.DEFAULT_TYPE
) -> Job:
    try:
        coin = context.args[0]
        timeframe = int(context.args[1])
        if timeframe not in TIMEFRAMES:
            raise ValueError('timeframe invalid value')
        setpoint = int(context.args[2])
    except Exception:
        await context.bot.send_message(
            chat_id=chat_id,
            text='Usage: /add rsi <coin> <timeframe> <setpoint>'
        )
    else:
        job_name = rsi_job_name(user_id, coin, timeframe, setpoint)
        jobs = context.job_queue.get_jobs_by_name(job_name)
        if jobs:
            text = '\n'.join(
                [f'Remove {job_title(job)} job' for job in jobs]
            ) + '\n'
            for job in jobs:
                job.schedule_removal()
        else:
            text = ''
        result = context.job_queue.run_repeating(
            callback=rsi_job,
            interval=RSI_JOB_INTERVAL,
            name=job_name,
            chat_id=chat_id,
            user_id=user_id,
            data={
                'type': RSI_JOB,
                'coin': coin,
                'timeframe': timeframe,
                'setpoint': setpoint,
            }
        )
        await context.bot.send_message(
            chat_id=chat_id,
            text=text + f'Add {job_title(result)} job'
        )
        return result


async def add_atr_job(
    user_id: int,
    chat_id: int,
    context: ContextTypes.DEFAULT_TYPE
) -> Job:
    try:
        coin = context.args[0]
        timeframe = int(context.args[1])
        if timeframe not in TIMEFRAMES:
            raise ValueError('timeframe invalid value')
        setpoint = int(context.args[2])
    except Exception:
        await context.bot.send_message(
            chat_id=chat_id,
            text='Usage: /add atr <coin> <timeframe> <setpoint>'
        )
    else:
        job_name = atr_job_name(user_id, coin, timeframe, setpoint)
        jobs = context.job_queue.get_jobs_by_name(job_name)
        if jobs:
            text = '\n'.join(
                [f'Remove {job_title(job)} job' for job in jobs]
            ) + '\n'
            for job in jobs:
                job.schedule_removal()
        else:
            text = ''
        result = context.job_queue.run_repeating(
            callback=atr_job,
            interval=ATR_JOB_INTERVAL,
            name=job_name,
            chat_id=chat_id,
            user_id=user_id,
            data={
                'type': ATR_JOB,
                'coin': coin,
                'timeframe': timeframe,
                'setpoint': setpoint,
            }
        )
        await context.bot.send_message(
            chat_id=chat_id,
            text=text + f'Add {job_title(result)} job'
        )
        return result


async def add_poc_job(
    user_id: int,
    chat_id: int,
    context: ContextTypes.DEFAULT_TYPE
) -> Job:
    try:
        coin = context.args[0]
        timeframe = int(context.args[1])
    except Exception:
        await context.bot.send_message(
            chat_id=chat_id,
            text='Usage: /add poc <coin> <timeframe>'
        )
    else:
        job_name = poc_job_name(user_id, coin, timeframe)
        jobs = context.job_queue.get_jobs_by_name(job_name)
        if jobs:
            text = '\n'.join(
                [f'Remove {job_title(job)} job' for job in jobs]
            ) + '\n'
            for job in jobs:
                job.schedule_removal()
        else:
            text = ''
        result = context.job_queue.run_repeating(
            callback=poc_job,
            interval=POC_JOB_INTERVAL,
            name=job_name,
            chat_id=chat_id,
            user_id=user_id,
            data={
                'type': POC_JOB,
                'coin': coin,
                'timeframe': timeframe,
            }
        )
        await context.bot.send_message(
            chat_id=chat_id,
            text=text + f'Add {job_title(result)} job'
        )
        return result


async def add_trend_job(
    user_id: int,
    chat_id: int,
    context: ContextTypes.DEFAULT_TYPE
) -> Job:
    pass


def find_jobs(
    queue: JobQueue,
    user_id: int,
    job_type: str = None
) -> list[Job]:
    if job_type is None:
        return [
            job for job in queue.jobs()
            if job.user_id == user_id
        ]
    return [
        job for job in queue.jobs()
        if job.user_id == user_id and job.data['type'] == job_type
    ]


def remove_job(queue: JobQueue, name: str) -> None:
    for job in queue.get_jobs_by_name(name):
        job.schedule_removal()


def remove_jobs(queue: JobQueue, user_id: int, job_type: str = None):
    for job in find_jobs(queue, user_id, job_type):
        job.schedule_removal()


async def remove_rsi_job(
    user_id: int,
    chat_id: int,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    try:
        coin = context.args[0]
        timeframe = int(context.args[1])
        setpoint = int(context.args[2])
    except Exception:
        await context.bot.send_message(
            chat_id=chat_id,
            text='Usage: /remove rsi <coin> <timeframe> <setpoint>'
        )
    else:
        job_name = rsi_job_name(user_id, coin, timeframe, setpoint)
        jobs = context.job_queue.get_jobs_by_name(job_name)
        if jobs:
            text = '\n'.join([f'Remove {job_title(job)} job' for job in jobs])
            for job in jobs:
                job.schedule_removal()
        else:
            text = 'empty'
        await context.bot.send_message(
            chat_id=chat_id,
            text=text
        )


async def remove_atr_job(
    user_id: int,
    chat_id: int,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    try:
        coin = context.args[0]
        timeframe = int(context.args[1])
        setpoint = int(context.args[2])
    except Exception:
        await context.bot.send_message(
            chat_id=chat_id,
            text='Usage: /remove atr <coin> <timeframe> <setpoint>'
        )
    else:
        job_name = atr_job_name(user_id, coin, timeframe, setpoint)
        jobs = context.job_queue.get_jobs_by_name(job_name)
        if jobs:
            text = '\n'.join([f'Remove {job_title(job)} job' for job in jobs])
            for job in jobs:
                job.schedule_removal()
        else:
            text = 'empty'
        await context.bot.send_message(
            chat_id=chat_id,
            text=text
        )


async def remove_poc_job(
    user_id: int,
    chat_id: int,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    try:
        coin = context.args[0]
        timeframe = int(context.args[1])
    except Exception:
        await context.bot.send_message(
            chat_id=chat_id,
            text='Usage: /remove atr <coin> <timeframe>'
        )
    else:
        job_name = poc_job_name(user_id, coin, timeframe)
        jobs = context.job_queue.get_jobs_by_name(job_name)
        if jobs:
            text = '\n'.join([f'Remove {job_title(job)} job' for job in jobs])
            for job in jobs:
                job.schedule_removal()
        else:
            text = 'empty'
        await context.bot.send_message(
            chat_id=chat_id,
            text=text
        )


async def remove_trend_job(
    user_id: int,
    chat_id: int,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    pass


async def add_command_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    try:
        job_type = context.args.pop(0).lower()
        if job_type == RSI_JOB:
            await add_rsi_job(user_id, chat_id, context)
        elif job_type == ATR_JOB:
            await add_atr_job(user_id, chat_id, context)
        elif job_type == POC_JOB:
            await add_poc_job(user_id, chat_id, context)
        elif job_type == TREND_JOB:
            await add_trend_job(user_id, chat_id, context)
        else:
            raise ValueError('job_type invalid value')
    except Exception:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(f'Usage: /add <job_type>\njob_type: {RSI_JOB}, {ATR_JOB}, '
                  f'{POC_JOB}, {TREND_JOB}, {ALL_JOBS}')
        )


async def remove_command_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    try:
        job_type = context.args.pop(0).lower()
        if job_type == RSI_JOB:
            await remove_rsi_job(user_id, chat_id, context)
        elif job_type == ATR_JOB:
            await remove_atr_job(user_id, chat_id, context)
        elif job_type == POC_JOB:
            await remove_poc_job(user_id, chat_id, context)
        elif job_type == TREND_JOB:
            await remove_trend_job(user_id, chat_id, context)
        elif job_type == ALL_JOBS:
            remove_jobs(context.job_queue, user_id)
        else:
            raise ValueError('job_type invalid value')
    except Exception:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(f'Usage: /remove <job_type>\njob_type: {RSI_JOB}, '
                  f'{ATR_JOB}, {POC_JOB}, {TREND_JOB}, {ALL_JOBS}')
        )


async def list_command_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    try:
        job_type = context.args.pop(0).lower()
        if job_type == RSI_JOB:
            jobs = find_jobs(context.job_queue, user_id, RSI_JOB)
        elif job_type == ATR_JOB:
            jobs = find_jobs(context.job_queue, user_id, ATR_JOB)
        elif job_type == POC_JOB:
            jobs = find_jobs(context.job_queue, user_id, POC_JOB)
        elif job_type == TREND_JOB:
            jobs = find_jobs(context.job_queue, user_id, TREND_JOB)
        elif job_type == ALL_JOBS:
            jobs = find_jobs(context.job_queue, user_id)
        else:
            raise ValueError('job_type invalid value')
    except Exception:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(f'Usage: /list <job_type>\njob_type: {RSI_JOB}, {ATR_JOB}, '
                  f'{POC_JOB}, {TREND_JOB}, {ALL_JOBS}')
        )
    else:
        text = '\n'.join([job_title(job) for job in jobs]) or 'empty'
        await context.bot.send_message(
            chat_id=chat_id,
            text=text
        )


def build_bot_application() -> Application:
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(
        CommandHandler('add', add_command_handler)
    )
    app.add_handler(
        CommandHandler('remove', remove_command_handler)
    )
    app.add_handler(
        CommandHandler('list', list_command_handler)
    )
    return app


def run_bot_application(app: Application) -> None:
    app.run_polling(allowed_updates=Update.ALL_TYPES)

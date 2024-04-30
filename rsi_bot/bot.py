import logging

from telegram import (
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from rsi_bot import settings
from rsi_bot.exceptions import (
    BotJobsShellError,
)
from rsi_bot.jobs import (
    BotJobHelper,
    BotJobsShell,
)

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = settings.Enviroment().telegram_token


async def jobs_callback(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job.data
    if isinstance(job, BotJobHelper):
        message = await job.execute()
        if message:
            await context.bot.send_message(
                chat_id=context.job.chat_id,
                text=message
            )


async def add_command_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    try:
        message = BotJobsShell.add_job(
            args=context.args,
            user_id=user_id,
            chat_id=chat_id,
            queue=context.job_queue,
            callback=jobs_callback,
        )
    except BotJobsShellError as error:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f'Usage: /add {str(error)}'
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=message
        )


async def remove_command_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    try:
        message = BotJobsShell.remove_job(
            args=context.args,
            user_id=user_id,
            queue=context.job_queue
        )
    except BotJobsShellError as error:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f'Usage: /remove {str(error)}'
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=message or 'empty'
        )


async def list_command_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    try:
        message = BotJobsShell.jobs_list(
            args=context.args,
            user_id=user_id,
            queue=context.job_queue,
        )
    except BotJobsShellError as error:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f'Usage: /list {str(error)}'
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=message or 'empty'
        )


async def errors_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    error = context.error
    text = [str(type(error))]
    while error.__cause__ is not None:
        error = error.__cause__
        text.append(str(type(error)))
    logger.error(f'{" - ".join(text)}: {str(error)}')


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
    app.add_error_handler(errors_handler)
    return app


def run_bot_application(app: Application) -> None:
    app.run_polling(allowed_updates=Update.ALL_TYPES)

from contextlib import suppress

from aiogram import Dispatcher
from aiogram.utils.exceptions import TelegramAPIError
from aiogram.utils.executor import Executor
from loguru import logger

from app import config
from app.config import SUPER_USER_ID
from app.misc import dp
from app.services import apscheduller, join_list

runner = Executor(dp)


async def on_startup_notify(dispatcher: Dispatcher):
    with suppress(TelegramAPIError):
        await dispatcher.bot.send_message(
            chat_id=SUPER_USER_ID, text="Bot started", disable_notification=True
        )
        logger.info("Notified superuser about bot is started.")


def setup():
    logger.info("Configure executor...")
    join_list.setup(runner)
    apscheduller.setup(runner)
    if config.SUPERUSER_STARTUP_NOTIFIER:
        runner.on_startup(on_startup_notify)

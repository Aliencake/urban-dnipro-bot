from aiogram import Dispatcher
# from aiogram.contrib.middlewares.logging import LoggingMiddleware
from loguru import logger


def setup(dispatcher: Dispatcher):
    logger.info("Configure middlewares...")

    # dispatcher.middleware.setup(LoggingMiddleware("bot"))

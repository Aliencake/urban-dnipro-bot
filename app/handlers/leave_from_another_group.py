from contextlib import suppress

from aiogram import exceptions, types
from loguru import logger

from app.config import SUPER_USER_ID, URBAN_DP_ID
from app.misc import dp


@dp.message_handler(content_types=types.ContentTypes.GROUP_CHAT_CREATED)
async def auto_leave(message: types.Message):
    chat_id = message.chat.id
    if chat_id != URBAN_DP_ID:
        with suppress(exceptions.TelegramAPIError):
            await message.answer("лолкек")
        with suppress(exceptions.TelegramAPIError):
            await dp.bot.leave_chat(chat_id)
        msg = f"Urban_bot leaved from chat {message.chat}"
        await dp.bot.send_message(SUPER_USER_ID, msg)
        logger.info(msg)

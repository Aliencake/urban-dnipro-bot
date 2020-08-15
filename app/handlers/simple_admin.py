from datetime import timedelta

from aiogram import types
from aiogram.utils import exceptions
from aiogram.utils.markdown import hlink
from loguru import logger

from app.config import SUPER_USER_ID
from app.misc import bot, dp


@dp.message_handler(
    regexp=r"^!ro.*$",
    is_reply=True,
    user_can_restrict_members=True,
    bot_can_restrict_members=True,
)
async def cmd_ro(message: types.Message):
    minutes = message.text.split("!ro")[1]
    logger.info(minutes)
    if not minutes:
        minutes = 15
    logger.info(minutes)
    duration = timedelta(minutes=int(minutes))
    try:  # Apply restriction
        await message.chat.restrict(
            message.reply_to_message.from_user.id, can_send_messages=False, until_date=duration
        )
        logger.info(
            "User {user} restricted by {admin} for {duration}",
            user=message.reply_to_message.from_user.id,
            admin=message.from_user.id,
            duration=duration,
        )
    except exceptions.BadRequest as e:
        logger.error("Failed to restrict chat member: {error!r}", error=e)
        return False

    await message.reply_to_message.answer(
        "{user} тобі заборонено писати повідомлення на <code>{duration}</code> хвилин".format(
            user=message.reply_to_message.from_user.get_mention(), duration=minutes,
        )
    )
    return True


@dp.message_handler(types.ChatType.is_group_or_super_group, text_contains="@admin")
@dp.message_handler(
    types.ChatType.is_group_or_super_group, commands=["report"], commands_prefix="!"
)
async def text_report_admins(message: types.Message):
    if not message.reply_to_message:
        return await message.reply(
            "Будь ласка, робіть реплай повідомлення, яке ви вважаєте неприємлимим"
        )
    logger.info(
        "User {user} report message {message} in chat {chat} from user {from_user}",
        user=message.from_user.id,
        message=message.message_id,
        chat=message.chat.id,
        from_user=message.reply_to_message.from_user.id,
    )
    text = "<b>[ALERT]</b> User {user} is reported message in chat {chat}.".format(
        user=message.from_user.get_mention(),
        chat=hlink(
            message.chat.title,
            f"https://t.me/c/{message.chat.id}/{message.reply_to_message.message_id}",
        )
        if not message.chat.username
        else hlink(
            message.chat.title,
            f"https://t.me/{message.chat.username}/{message.reply_to_message.message_id}",
        ),
    )

    await bot.send_message(SUPER_USER_ID, text)

    await message.reply_to_message.reply("<i>Адміністратори сповіщені</i>")

from aiogram import types
from aiogram.dispatcher.filters import CommandHelp, CommandStart
from aiogram.utils.markdown import hlink
from loguru import logger

from app import config
from app.misc import dp


@dp.message_handler(CommandStart())
async def cmd_start(message: types.Message):
    logger.info("User {user} start conversation with bot", user=message.from_user.id)
    await message.reply(
        "Вітаю !\n\n"
        f"Це бот для адміністрування чату {hlink('Urban Dnipro Сommunity', 'https://t.me/urban_comm')}"
        "\n\nЯкщо потрібна допомога, то натисніть команду /help\n\n"
        f"Розробник боту - "
        f"{'@aliencake' if message.chat.type == types.ChatType.PRIVATE else '<code>@aliencake</code>'}"
        f"\n\n"
        "<i>Допомогти бідному студенту</i> - /donate",
        disable_web_page_preview=True,
    )


@dp.message_handler(CommandHelp())
async def cmd_help(message: types.Message):
    logger.info("User {user} asked for help", user=message.from_user.id)
    commands = ""
    for command in await dp.bot.get_my_commands():
        commands += f"/{command.command} - <i>{command.description}</i>\n\n"

    await message.reply(
        "<b>Доступний функціонал бота:</b>\n\n"
        f"{commands}"
        "!report або @admin - <i>повідомити адміністраторів о порушенні правил чату</i>\n\n"
        "<b>Для адміністраторів:</b>\n\n"
        "!ro10 - <i>позбавлення можливості писати повідомлення на термін у <code>10</code> хвилин</i>"
    )


@dp.message_handler(commands=["donate"])
async def cmd_donate(message: types.Message):
    logger.info("User {user} wanna donate", user=message.from_user.id)
    await message.reply(
        '<i>"Бот потребує місце для життя, а студент має потребу у кофеїні"</i>\n\n'
        "Якщо маєте зайву копієчку, або просто бажаєте порадувати бідного студента та покрити оплату "
        "сервера - можете задонатити на банківську картку:\n\n"
        "<code>5375 4141 0433 0591</code>\n\n"
        "<i>Щиро дякую за підтримку!</i>"
    )


@dp.errors_handler()
async def errors_handler(update: types.Update, exception: Exception):
    try:
        raise exception
    except Exception as e:
        logger.exception("Cause exception {e} in update {update}", e=e, update=update)
        await dp.bot.send_message(chat_id=config.SUPER_USER_ID, text=e)
    return True

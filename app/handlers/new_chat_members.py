import asyncio
import datetime
import os
import random
from contextlib import suppress

from aiogram import exceptions, types
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import BadRequest, MessageToDeleteNotFound
from aiogram.utils.markdown import hcode, hlink, quote_html
from emoji import demojize, emojize
from loguru import logger
from PIL import Image

from app import config
from app.misc import dp
from app.services.join_list import join_list

cb_join_list = CallbackData("join_chat", "answer")


@dp.message_handler(content_types=types.ContentTypes.NEW_CHAT_MEMBERS)
async def new_chat_member(message: types.Message):
    chat_id = message.chat.id
    rules_link = hlink("ПРАВИЛА ЧАТУ", config.RULES_MSG_LINK)
    if message.date < datetime.datetime.now() - datetime.timedelta(minutes=1):
        logger.warning(
            "Join message {message} is too old. Skip filtering. (Age: {age})",
            message=message.message_id,
            age=datetime.datetime.now() - message.date,
        )
        return False
    users = {}
    for new_member in message.new_chat_members:
        try:
            chat_member = await message.chat.get_member(new_member.id)
            if new_member.is_bot:
                if new_member.id == dp.bot.id:
                    if chat_id != config.URBAN_DP_ID:
                        with suppress(exceptions.TelegramAPIError):
                            await message.answer(hcode("лолкек"))
                        with suppress(exceptions.TelegramAPIError):
                            await dp.bot.leave_chat(chat_id)
                    msg = (
                        f"User {hlink(f'{message.from_user.full_name}', f'tg://user?id={message.from_user.id}')} "
                        f"was trying to add urban_bot to the chat {message.chat}"
                    )
                    await dp.bot.send_message(config.SUPER_USER_ID, msg)
                    logger.info(msg)
                    return False
            elif chat_member.status == "restricted":
                pass
            else:
                await message.chat.restrict(
                    new_member.id, permissions=types.ChatPermissions(can_send_messages=False)
                )
                users[new_member.id] = new_member.get_mention()
        except BadRequest as e:
            logger.error(
                "Cannot restrict chat member {user} with error: {error}",
                user=new_member.id,
                error=e,
            )
            continue
    if not users:
        return False

    emojis = [
        "🍏",
        "🍎",
        "🍐",
        "🍊",
        "🍋",
        "🍌",
        "🍉",
        "🍇",
        "🍓",
        "🍈",
        "🍒",
        "🍑",
        "🥭",
        "🍍",
        "🥥",
        "🥝",
        "🍅",
        "🍆",
        "🥑",
        "🥦",
        "🥬",
        "🥒",
        "🌶",
        "🌽",
        "🥕",
    ]

    right_emoji = random.choice(os.listdir("/app/app/pictures/emojis"))

    right_emoji_pic = Image.open(f"/app/app/pictures/emojis/{right_emoji}")

    background: Image = Image.open("/app/app/pictures/ud_logo.jpg")

    if random.randrange(2):
        background.paste(
            right_emoji_pic,
            (random.randrange(20, 530, 30), random.randrange(20, 100, 30)),
            right_emoji_pic,
        )
    else:
        background.paste(
            right_emoji_pic,
            (random.randrange(20, 530, 30), random.randrange(450, 530, 30)),
            right_emoji_pic,
        )

    background.save("captcha.jpg")

    right_answer_marker = True

    buttons_menu = []
    for _ in range(3):
        buttons = []
        for _ in range(3):
            if right_answer_marker:
                emoji = emojize(f":{right_emoji.split('.png')[0]}:")
                await dp.storage.update_data(
                    chat=message.chat.id,
                    user=None,
                    data={f"right_answer-{message.message_id}": emoji},
                )
                buttons.append(
                    types.InlineKeyboardButton(emoji, callback_data=cb_join_list.new(answer=emoji))
                )
                emojis.remove(emoji)
                right_answer_marker = False
            else:
                emoji = random.choice(emojis)
                buttons.append(
                    types.InlineKeyboardButton(emoji, callback_data=cb_join_list.new(answer=emoji))
                )
                emojis.remove(emoji)
        random.shuffle(buttons)
        buttons_menu.append(buttons)
    random.shuffle(buttons_menu)
    msg = await message.reply_photo(
        caption="{users}, вітаємо вас у чаті <b>{chat}</b>\n\n"
        "Будь ласка, прочитайте правила, що вказані у посиланні нижче\n\n"
        "{link}\n\n"
        "Якщо ви погоджуєтесь з ними, то натисніть на кнопку емоджі"
        ", що вказано на зображенні вище\n\n"
        "У вас є <code>5</code> хвилин на натискання, інакше, вас автоматично виженуть "
        "із чату".format(
            users=", ".join(users.values()),
            chat=quote_html(message.chat.full_name),
            link=rules_link,
        ),
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons_menu),
        photo=types.InputFile("captcha.jpg"),
    )
    await join_list.create_list(
        chat_id=message.chat.id, message_id=msg.message_id, users=users.keys()
    )
    background.close()

    os.remove("captcha.jpg")

    return True


@dp.callback_query_handler(cb_join_list.filter())
async def cq_join_list(query: types.CallbackQuery, callback_data: dict):
    answer = callback_data["answer"]
    in_list = await join_list.pop_user_from_list(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        user_id=query.from_user.id,
    )
    if not in_list:
        return await query.answer("Це не для тебе!", show_alert=True)
    get_right_answer = await dp.storage.get_data(chat=query.message.chat.id, user=None)
    right_answer = get_right_answer[f"right_answer-{query.message.message_id-1}"]
    if answer == right_answer:
        await query.answer("Чудово!\nТепер ви можете писати у чат")
        await query.message.chat.restrict(
            query.from_user.id,
            permissions=types.ChatPermissions(can_send_messages=True),
            until_date=config.JOIN_NO_MEDIA_DURATION,
        )
        logger.info(
            "User {user} choose right answer {answer} in join-list in chat {chat} and message {message}",
            user=query.from_user.id,
            chat=query.message.chat.id,
            answer=demojize(answer),
            message=query.message.message_id,
        )
    else:
        await query.answer("Невірна відповідь", show_alert=True)
        await asyncio.sleep(2)
        await query.message.chat.unban(query.from_user.id)
        logger.info(
            "User {user} choose wrong answer {answer} in join-list in chat {chat} and message {message} and get banned",
            user=query.from_user.id,
            chat=query.message.chat.id,
            answer=demojize(answer),
            message=query.message.message_id,
        )
    users_list = await join_list.check_list(
        chat_id=query.message.chat.id, message_id=query.message.message_id
    )
    if not users_list:
        with suppress(MessageToDeleteNotFound):
            await query.message.delete()

    return True

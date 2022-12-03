from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from dependency_injector.wiring import inject, Provide

from loguru import logger

from src.config.messages import Start, Buttons
from src.container import Container
from src.dto.user import User
from src.storage.cache import Cache


@inject
async def start_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    cache: Cache = Provide[Container.cache],
    default_admins: list[int] = Provide[Container.config.provided.default_admins],
    msgs: Start = Provide[Container.messages.provided.start],
    btns: Buttons = Provide[Container.messages.provided.buttons],
) -> None:
    """
    Start message for users
    """
    user = User(
        tg_id=update.effective_user.id,
        name=update.effective_user.name,
        admin=update.effective_user.id in default_admins
    )
    u = await cache.get_user_by(user.tg_id, user.name, first=True)
    if u:
        msg = msgs.if_exist + msgs.if_exist_without_phone if not u.phone else ''
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=str(msg),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(btns.send_phone, request_contact=True),
                    ],
                ],
                resize_keyboard=True,
                one_time_keyboard=True,
            ) if not u.phone else None
        )
        return

    _ = await cache.save_user(user)
    logger.info('Save new user: {}'.format(user))

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msgs.first,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(btns.send_phone, request_contact=True),
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    )

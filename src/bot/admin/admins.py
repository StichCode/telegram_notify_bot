from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from dependency_injector.wiring import inject, Provide
from loguru import logger

from src.container import Container
from src.storage.cache import Cache
from src.storage.enums import CallbackKeys, KeysStorage, StagesUser


@inject
async def admins_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    cache: Cache = Provide[Container.cache]
) -> None:
    if not await cache.is_admin(update.effective_user.id):
        logger.info('User {} try to get admins route'.format(update.effective_user.name))
        return

    context.user_data[KeysStorage.stage] = StagesUser.administration
    await context.bot.send_message(
        update.effective_chat.id,
        text='Что бы хотите сделать?',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton("Добавить администратора", callback_data=CallbackKeys.create_admin),
                    InlineKeyboardButton("Удалить администратора", callback_data=CallbackKeys.delete_admin)
                ]
            ],
        )
    )

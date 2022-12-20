from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from dependency_injector.wiring import inject, Provide
from loguru import logger

from config.messages import Messages
from src.container import Container
from src.storage.cache import Cache
from src.storage.enums import CallbackKeys, KeysStorage, StagesUser


@inject
async def admins_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    cache: Cache = Provide[Container.cache],
    msgs: Messages = Provide[Container.messages]
) -> None:
    if not await cache.is_admin(update.effective_user.id):
        logger.info('User {} try to get admins route'.format(update.effective_user.name))
        return

    context.user_data[KeysStorage.stage] = StagesUser.administration
    await context.bot.send_message(
        update.effective_chat.id,
        text=msgs.admins.first,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(msgs.buttons.add_admin, callback_data=CallbackKeys.create_admin),
                    InlineKeyboardButton(msgs.buttons.delete_admin, callback_data=CallbackKeys.delete_admin)
                ]
            ],
        )
    )

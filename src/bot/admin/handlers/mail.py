from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from dependency_injector.wiring import inject, Provide

from loguru import logger

from config.messages import Mail
from src.container import Container
from src.storage.cache import Cache
from src.storage.enums import KeysStorage, StagesUser


@inject
async def mail_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    cache: Cache = Provide[Container.cache],
    msgs: Mail = Provide[Container.messages.provided.mail]
) -> None:
    if not await cache.is_admin(update.effective_user.id):
        logger.info('User {} try to get admins route'.format(update.effective_user.name))
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msgs.first,
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data[KeysStorage.stage] = StagesUser.create_message

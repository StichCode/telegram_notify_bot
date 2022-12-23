from dependency_injector.wiring import inject, Provide
from loguru import logger

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config.messages import Help
from src.container import Container
from src.storage.cache import Cache


@inject
async def help_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    cache: Cache = Provide[Container.cache],
    msgs: Help = Provide[Container.messages.provided.help]
) -> None:
    is_admin = await cache.is_admin(update.effective_user.id)
    logger.debug('user: {}, is_admin: {}'.format(update.effective_user.id, is_admin))
    text = msgs.message
    commands = msgs.user.copy()
    if is_admin:
        commands.update(msgs.admin)
    for k, v in commands.items():
        text += """*/{0:10s}* {1}\n""".format(k, v)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=ReplyKeyboardRemove(),
    )

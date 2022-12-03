import prettytable as pt

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from dependency_injector.wiring import inject, Provide

from loguru import logger

from src.config.messages import Users
from src.container import Container
from src.storage.cache import Cache


@inject
async def users_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    cache: Cache = Provide[Container.cache],
    msgs: Users = Provide[Container.messages.provided.users]
) -> None:
    if not await cache.is_admin(update.effective_user.id):
        logger.info('User {} try to get admins route'.format(update.effective_user.name))
        return
    tb = pt.PrettyTable(msgs.columns)
    users = await cache.get_all_users()
    for u in users:
        tb.add_row([u.name, f"{'Y' if u.phone else 'N':1s}", f"{'Y' if u.admin else 'N':1s}"])

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msgs.message.format(len(users), f"```{tb}```"),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=ReplyKeyboardRemove()
    )

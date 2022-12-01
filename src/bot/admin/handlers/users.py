from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from dependency_injector.wiring import inject, Provide

from loguru import logger

from src.container import Container
from src.storage.cache import Cache


@inject
async def users_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    cache: Cache = Provide[Container.cache]
) -> None:
    """
    :param update:
    :param context:
    :param cache:
    :return:
    """
    if not await cache.is_admin(update.effective_user.id):
        logger.info('User {} try to get admins route'.format(update.effective_user.name))
        return

    users = [
        f"{u.name:15s}{'':3s}Number: {'Y' if u.phone else 'N':3s}, Admin: {'Y' if u.admin else 'N':3s} "
        for u in await cache.get_all_users()
    ]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Количество пользователей в базе: {}\nПользователи:\n{}'.format(len(users), "\n".join(users)),
        reply_markup=ReplyKeyboardRemove()
    )

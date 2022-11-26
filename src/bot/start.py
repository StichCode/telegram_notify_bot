from telegram import Update
from telegram.ext import ContextTypes
from dependency_injector.wiring import inject, Provide

from loguru import logger

from src.container import Container
from src.dto.user import User
from src.storage.cache import Cache


@inject
async def start_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    cache: Cache = Provide[Container.cache]
) -> None:
    """
    Start message for users
    :param cache:
    :param update:
    :param context:
    :return:
    """
    user = User(
        tg_id=update.effective_user.id,
        # todo: do this by validator
        name=update.effective_user.name.replace('@', '')
    )
    u = await cache.get_user_by(user.tg_id, user.name)
    if u and len(u) > 0 and u[0]:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вы уже подписаны на нашу рассылку, как только мы будем готовы мы вам напишем!\n\n'
                 'С любовью @trip_for_students 🧡',
        )
        return

    _ = await cache.save_user(user)
    logger.info('Save new user: {}'.format(user))

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Спасибо что подписались на нас!\n'
             'Как только мы будем готовы, мы сообщим вам!\n\n'
             'С любовью @trip_for_students 🧡',
        )

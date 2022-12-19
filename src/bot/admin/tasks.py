from loguru import logger

from telegram.ext import ContextTypes

from src.container import Container
from src.dto.user import User
from src.storage.cache import Cache
from dependency_injector.wiring import inject, Provide


async def tfs_notify_task(
    context: ContextTypes.DEFAULT_TYPE,
    users: list[User],
    message: str,
) -> int:
    """
    Notify all users
    :return:
    """
    sends = 0
    not_send = []
    for user in users:
        try:
            await context.bot.send_message(
                chat_id=user.tg_id,
                text=message,
            )
            sends += 1
            logger.info('send {} message: {}'.format(user.tg_id, message))
        except Exception as ex:
            logger.exception(ex)
            not_send.append(user)
    logger.info('Sends {0}/{1}'.format(sends, len(users)))
    # return info about not send to users
    return sends


@inject
async def create_db(
    _: ContextTypes.DEFAULT_TYPE,
    cache: Cache = Provide[Container.cache]
) -> None:
    """
    init db
    :return:
    """
    await cache.init_db()
    logger.info('init db complete')

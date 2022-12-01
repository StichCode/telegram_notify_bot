from loguru import logger

from telegram.ext import ContextTypes

from src.dto.user import User


async def tfs_notify_task(
    context: ContextTypes.DEFAULT_TYPE,
    users: list[User],
    message: str,
) -> None:
    """
    Notify all users
    :return:
    """
    sends = 0
    total = len(users)
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

    logger.info('Sends {0}/{1}'.format(sends, total))

from loguru import logger

from telegram.ext import ContextTypes


async def tfs_notify_task(
    context: ContextTypes.DEFAULT_TYPE,
    message, users
) -> None:
    """
    Notify all users

    :return:
    """
    sends = 0
    not_sends = 0
    for user in users:
        try:
            await context.bot.send_message(
                chat_id=user,
                text=message,
            )
            sends += 1
        except Exception as ex:
            logger.exception(ex)
            not_sends += 1

    logger.info('Sends {}, not sends {}'.format(sends, not_sends))

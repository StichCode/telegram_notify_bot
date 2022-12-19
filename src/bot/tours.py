import pandas as pd
from dependency_injector.wiring import Provide, inject
from loguru import logger
from telegram import Update, ReplyKeyboardRemove
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config.config import GoogleExcelConfig
from src.bot.functions.get_nearest_tours import get_prettify_data
from src.container import Container
from src.storage.cache import Cache


@inject
async def tours_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    cache: Cache = Provide[Container.cache],
    cfg: GoogleExcelConfig = Provide[Container.config.provided.google_cfg]
) -> None:
    if not await cache.is_admin(update.effective_user.id):
        logger.info('User {} try to get admins route'.format(update.effective_user.name))
        return
    # tb = get_prettify_data(cfg)
    # if tb:
    #     await context.bot.send_message(
    #         chat_id=update.effective_chat.id,
    #         text='Ближайшие туры в которые вы можете поехать с нами:\n ```{}```'.format(tb),
    #         parse_mode=ParseMode.MARKDOWN_V2,
    #         reply_markup=ReplyKeyboardRemove()
    #     )
    # else:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        # todo: adding notify if no free tours, when get new free tour
        text='В ближайшее время нет свободных мест, но как только появятся мы вам сообщим 🧡',
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=ReplyKeyboardRemove()
    )

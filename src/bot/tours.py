import pandas as pd
from dependency_injector.wiring import Provide, inject
from loguru import logger
from telegram import Update, ReplyKeyboardRemove
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

# from src.bot.functions.get_nearest_tours import get_xlsx_data, prettify_data
from src.container import Container
from src.storage.cache import Cache


@inject
async def tours_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    cache: Cache = Provide[Container.cache],
) -> None:
    if not await cache.is_admin(update.effective_user.id):
        logger.info('User {} try to get admins route'.format(update.effective_user.name))
        return
    # d_values = get_xlsx_data()
    # columns = ['month', 'num', 'name', 'buy', 'total']
    # table = prettify_data(pd.DataFrame(d_values[0:], columns=columns))

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Ближайшие туры с свободными местечками: {}",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=ReplyKeyboardRemove()
    )

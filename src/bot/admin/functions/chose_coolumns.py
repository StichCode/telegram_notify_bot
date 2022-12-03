from telegram import CallbackQuery
from telegram.ext import ContextTypes

from loguru import logger

from src.bot.admin.functions.verification_xlsx_file import verify_xlsx
from src.storage.enums import CallbackKeys, KeysStorage


async def choose_columns(
    context: ContextTypes.DEFAULT_TYPE,
    choice: str,
    callback_query: CallbackQuery,
    cache
) -> None:
    if CallbackKeys.column_phone in choice:
        context.user_data[KeysStorage.column_phone] = choice.split('_')[0]
        return await verify_xlsx(context, callback_query, cache)
    else:
        logger.error(choice)
    return

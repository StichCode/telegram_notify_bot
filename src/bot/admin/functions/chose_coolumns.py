from telegram import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telegram.ext import ContextTypes

from loguru import logger

from src.bot.admin.functions.verification_xlsx_file import verify_xlsx
from src.bot.admin.utils import get_xlsx, to_sublist
from src.storage.enums import CallbackKeys, KeysStorage


async def choose_columns(
    context: ContextTypes.DEFAULT_TYPE,
    choice: str,
    callback_query: CallbackQuery,
    cache
) -> None:
    df = get_xlsx(context.user_data[KeysStorage.file_path])
    if CallbackKeys.column_name in choice:
        context.user_data[KeysStorage.column_name] = choice.split('_')[0]
        btns = to_sublist(
            [
                InlineKeyboardButton(c, callback_data="{}_{}".format(c, CallbackKeys.column_phone))
                for c in (df.columns.to_list())
            ]
        )
        await context.bot.edit_message_text(
            chat_id=callback_query.message.chat_id,
            message_id=callback_query.message.message_id,
            text='Колонка с именами пользователей выбрана,\n'
                 'теперь надо выбрать колонку с номер телефона:',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=btns)
        )
    elif CallbackKeys.column_phone in choice:
        context.user_data[KeysStorage.column_phone] = choice.split('_')[0]
        return await verify_xlsx(context, callback_query, cache)
    else:
        logger.error(choice)
    return

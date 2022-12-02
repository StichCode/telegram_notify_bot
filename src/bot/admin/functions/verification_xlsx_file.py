from telegram import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from loguru import logger

from src.bot.admin.utils import get_file, merge_users
from src.dto.user_data import UserData
from src.errors import BadColumnName
from src.storage.cache import Cache
from src.storage.enums import CallbackKeys


async def verify_xlsx(
    context: ContextTypes.DEFAULT_TYPE,
    callback_query: CallbackQuery,
    cache: Cache
) -> None:
    try:
        ud = UserData(**context.user_data)
    except ValueError as ex:
        logger.error(ex)
        await context.bot.edit_message_text(
            chat_id=callback_query.message.chat_id,
            message_id=callback_query.message.message_id,
            text='Что-то пошло не так, попробуйте сначала 🙈🙈🙈'
        )
        return

    try:
        users, bad_data = get_file(ud)
    except BadColumnName as ex:
        await context.bot.edit_message_text(
            chat_id=callback_query.message.chat_id,
            message_id=callback_query.message.message_id,
            text='При проверке xlsx, файла произошла ошибка,\n'
                 'выбранное вами поле {} не присутствует в xlsx файле.\n'
                 'Попробуйте снова, чуть позже, я пока сообщу администратору.'.format(ex.column)
        )
        return
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("Да", callback_data=CallbackKeys.sending),
                InlineKeyboardButton("Нет", callback_data=CallbackKeys.cancel)
            ]
        ],
    )
    if bad_data:
        await context.bot.edit_message_text(
            chat_id=callback_query.message.chat_id,
            message_id=callback_query.message.message_id,
            text='При проверке xlsx файла, '
                 'произошла ошибка при валидации этих пользователей:\n{}\n'
                 'Всё ещё хотите сделать рассылку на оставшихся пользователей? ({}/{})'
                 ''.format('\n'.join(bad_data), len(users), len(bad_data)),
            reply_markup=keyboard
        )
        return

    db_users = await cache.get_all_users()
    merged = merge_users(db_users, users)
    if len(users) == 0:
        pass
    if len(users) != len(merged):
        await context.bot.edit_message_text(
            chat_id=callback_query.message.chat_id,
            message_id=callback_query.message.message_id,
            # tg_id -> 1, only for users from xlsx
            text='Некоторые из пользователей не подписаны на меня:\n{0}\n'
                 'Вы хотите сделать рассылку на оставшихся пользователей? ({1}/{2})'.format(
                '\n'.join([str(u) for u in users if u.tg_id == 1]),
                len(merged),
                len(users)
            ),
            reply_markup=keyboard
        )
        return
    await context.bot.edit_message_text(
        chat_id=callback_query.message.chat_id,
        message_id=callback_query.message.message_id,
        text='Все пользователи полученные в файле подписаны на меня 🧡\n'
             'Начинаю рассылку?',
        reply_markup=keyboard
    )

from telegram import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from dependency_injector.wiring import inject, Provide

from loguru import logger

from src.bot.admin.utils import get_file, merge_users
from config.messages import Messages
from src.container import Container
from src.dto.user_data import UserData
from src.errors import BadColumnName
from src.storage.cache import Cache
from src.storage.enums import CallbackKeys


@inject
async def verify_xlsx(
    context: ContextTypes.DEFAULT_TYPE,
    callback_query: CallbackQuery,
    cache: Cache,
    msgs: Messages = Provide[Container.messages]
) -> None:
    try:
        ud = UserData(**context.user_data)
    except ValueError as ex:
        logger.error(ex)
        await context.bot.edit_message_text(
            chat_id=callback_query.message.chat_id,
            message_id=callback_query.message.message_id,
            text=msgs.default_msg.stage_fail
        )
        return

    try:
        users, bad_data = get_file(ud)
    except BadColumnName as ex:
        logger.error(ex)
        await context.bot.edit_message_text(
            chat_id=callback_query.message.chat_id,
            message_id=callback_query.message.message_id,
            text=msgs.mail.xlsx_column_fail.format(ex.column)
        )
        return
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(msgs.buttons.default_yes, callback_data=CallbackKeys.sending),
                InlineKeyboardButton(msgs.buttons.default_no, callback_data=CallbackKeys.cancel)
            ]
        ],
    )
    if bad_data:
        await context.bot.edit_message_text(
            chat_id=callback_query.message.chat_id,
            message_id=callback_query.message.message_id,
            text=msgs.mail.bad_data.format('\n'.join(bad_data), len(users), len(bad_data)),
            reply_markup=keyboard
        )
        return

    db_users = await cache.get_all_users()
    merged = merge_users(db_users, users)
    if len(users) == 0:
        pass
    if len(users) != len(merged):
        if merged:
            await context.bot.edit_message_text(
                chat_id=callback_query.message.chat_id,
                message_id=callback_query.message.message_id,
                # tg_id -> 1, only for users from xlsx
                text=msgs.mail.not_subs.format(
                    '\n'.join([str(u) for u in users if u.tg_id == 1 and u.phone]),
                    len(merged), len(users)
                ),
                reply_markup=keyboard
            )
            return
        else:
            await context.bot.edit_message_text(
                chat_id=callback_query.message.chat_id,
                message_id=callback_query.message.message_id,
                # tg_id -> 1, only for users from xlsx
                text=msgs.mail.not_subs_all
            )
            return
    await context.bot.edit_message_text(
        chat_id=callback_query.message.chat_id,
        message_id=callback_query.message.message_id,
        text=msgs.mail.pre_send_msg,
        reply_markup=keyboard
    )

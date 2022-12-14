from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from dependency_injector.wiring import inject, Provide
from loguru import logger

from src.bot.admin.utils import get_xlsx, to_sublist
from config.messages import Messages
from src.container import Container
from src.storage.cache import Cache
from src.storage.enums import KeysStorage, StagesUser, CallbackKeys


@inject
async def callback_file_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    cache: Cache = Provide[Container.cache],
    msgs: Messages = Provide[Container.messages]
) -> None:
    if not await cache.is_admin(update.effective_user.id):
        logger.info('User {} try to get admins route'.format(update.effective_user.name))
        return

    stage = context.user_data[KeysStorage.stage]
    if stage not in [StagesUser.upload_file, StagesUser.pre_send]:
        logger.error('Something wrong with stage: {}'.format(stage))
        await context.bot.send_message(
            update.effective_user.id,
            text=msgs.default_msg.stage_fail
        )
        return

    doc = update.message.document
    if not doc and not doc.file_name.endswith('.xlsx'):
        await context.bot.send_message(
            update.effective_user.id,
            text=msgs.mail.bad_format_file
        )
        return

    file = await doc.get_file()
    context.user_data[KeysStorage.file_path] = file.file_path

    df = get_xlsx(file.file_path)
    btns = to_sublist(
        [
            InlineKeyboardButton(c, callback_data="{}_{}".format(c, CallbackKeys.column_phone))
            for c in (df.columns.to_list())
        ]
    )
    await context.bot.send_message(
        update.effective_chat.id,
        text=msgs.mail.choose_column_name,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=btns)
    )

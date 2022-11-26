from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from dependency_injector.wiring import inject, Provide
from loguru import logger

from src.bot.admin.utils import get_file
from src.container import Container
from src.storage.cache import Cache
from src.storage.enums import KeysStorage, StagesUser


@inject
async def callback_file_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    cache: Cache = Provide[Container.cache]
) -> None:
    if not await cache.is_admin(update.effective_user.id):
        logger.info('User {} try to get admins route'.format(update.effective_user.name))
        return

    stage = context.user_data.get(KeysStorage.stage, None)
    msg = context.user_data.get(KeysStorage.message, None)
    column_name = context.user_data.get(KeysStorage.column_name, None)

    if (stage is None or msg is None or column_name is None) or \
        stage not in [StagesUser.upload_file, StagesUser.pre_send]:
        logger.error('Something wrong with stage of user: {}'.format(stage))
        await context.bot.send_message(
            update.effective_user.id,
            text='Что то произошло на сервере, попробуйте начать сначала:c'
        )
        return

    doc = update.message.document
    if not doc and not doc.file_name.endswith('.xlsx'):
        await context.bot.send_message(
            update.effective_user.id,
            text='Вы прислали файл не правильного формата, попробуйте снова:3'
        )
        return

    file = await doc.get_file()
    context.user_data[KeysStorage.file_path] = file.file_path
    file_users = get_file(file.file_path, column_name)

    # todo: создать конфиг для админов
    db_users = await cache.get_all_users()
    unames = {u.name: u.tg_id for u in db_users}
    not_subscribe = set(file_users) - set(unames)

    # todo: сделать проверку если из файла не получилось достать людей сообщить об этом
    # todo: проверка если нет человек для нотифая не спрашивать никого
    if not_subscribe:
        context.user_data[KeysStorage.stage] = StagesUser.pre_send
        await context.bot.send_message(
            update.effective_chat.id,
            text='Эти пользователи не подписаны на бот ({1}/{2}) :\n{0}\n\n'
                 'Вы уверены что хотите сделать рассылку по оставшимся пользователям?'.format(
                    '\n'.join(not_subscribe),
                    len(file_users) - len(not_subscribe),
                    len(file_users)
                ),
            # todo: что бы там везде не ифать, думаю можно сделать колбэк из енама
            # todo: завести yaml с всеми сообщениями которые используются в боте
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton("Да", callback_data='1'),
                        InlineKeyboardButton("Нет", callback_data='0')
                    ]
                ],
            )
        )

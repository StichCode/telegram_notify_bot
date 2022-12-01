from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from dependency_injector.wiring import inject, Provide
from loguru import logger

from src.bot.admin.utils import get_file, merge_users
from src.container import Container
from src.storage.cache import Cache
from src.storage.enums import KeysStorage, StagesUser, CallbackKeys


@inject
async def callback_file_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    cache: Cache = Provide[Container.cache]
) -> None:
    if not await cache.is_admin(update.effective_user.id):
        logger.info('User {} try to get admins route'.format(update.effective_user.name))
        return

    for key in [KeysStorage.stage, KeysStorage.message, KeysStorage.column_name, KeysStorage.column_phone]:
        if key not in context.user_data:
            logger.error('Not found key: {}'.format(key))
            await context.bot.send_message(
                update.effective_user.id,
                text='Что то произошло на сервере, попробуйте начать сначала:c'
            )
            return

    stage = context.user_data[KeysStorage.stage]
    if stage not in [StagesUser.upload_file, StagesUser.pre_send]:
        logger.error('Something wrong with stage: {}'.format(stage))
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

    file_users = get_file(
        file.file_path,
        context.user_data[KeysStorage.column_name],
        context.user_data[KeysStorage.column_phone]
    )

    if file_users is None:
        text = 'Вы указали неверные названия колонок для excel, попробуй снова и больше внимательности!'
    elif not file_users:
        text = 'Вы отправили пустой файл? Я не нашел там никаких пользователей!'
    else:
        not_valid_numbers = len([u for u in file_users if u.phone is None])
        if not_valid_numbers >= 1:
            text = 'Не все пользователи были получены из списка, ' \
                   'не у всех пользователей номер телефона ' \
                   'в стандартном формате ({} шт.)'.format(not_valid_numbers)
        text = ''

    if text:
        await context.bot.send_message(
            update.effective_chat.id,
            text=text
        )
        return

    db_users = await cache.get_all_users()
    users = merge_users(db_users, file_users)
    if not users:
        del context.user_data[KeysStorage.stage]
        await context.bot.send_message(
            update.effective_chat.id,
            text='Я не нашел ни одного пользователя который был бы подписан на меня:c'
            )
        return

    uniq_users = set({(u.name, u.phone) for u in users})
    uniq_file_users = set({(u.name, u.phone) for u in file_users})
    not_subscribe = uniq_file_users - uniq_users

    # todo: сделать вывод информации о тех пользователях которые не распознались:/
    if not_subscribe:
        context.user_data[KeysStorage.stage] = StagesUser.pre_send
        await context.bot.send_message(
            update.effective_chat.id,
            text='Есть пользователи не подписанные на меня.\n'
                 'Вы уверены что хотите сделать рассылку по оставшимся пользователям? ({0}/{1})'.format(
                    len(users),
                    len(file_users)
                ),
            # todo: завести yaml с всеми сообщениями которые используются в боте
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton("Да", callback_data=CallbackKeys.sending),
                        InlineKeyboardButton("Нет", callback_data=CallbackKeys.cancel)
                    ]
                ],
            )
        )

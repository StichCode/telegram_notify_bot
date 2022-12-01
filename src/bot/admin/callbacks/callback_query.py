import asyncio
from functools import partial

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from dependency_injector.wiring import inject, Provide
from loguru import logger

from src.bot.admin.tasks import tfs_notify_task
from src.bot.admin.utils import get_file, merge_users
from src.container import Container
from src.dto.user_data import UserData
from src.storage.cache import Cache
from src.storage.enums import KeysStorage, StagesUser, CallbackKeys


@inject
async def callback_query_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    cache: Cache = Provide[Container.cache]
) -> None:
    q = update.callback_query
    await q.answer()
    choice = q.data

    if not await cache.is_admin(update.effective_user.id):
        logger.info('User {} try to get admins route'.format(update.effective_user.name))
        return

    stage = context.user_data.get(KeysStorage.stage, None)
    if stage is None:
        logger.error('Something wrong with stage of user: {}'.format(stage))
        await context.bot.send_message(
            update.effective_user.id,
            text='Что то произошло на сервере, попробуйте начать сначала:c'
        )
        return

    admins = await cache.get_all_users(only_admins=True)

    match choice:
        case CallbackKeys.cancel_msg:
            context.user_data[KeysStorage.stage] = StagesUser.create_message
            text = 'Введите сообщение по новой!'
        case CallbackKeys.accept_msg:
            context.user_data[KeysStorage.stage] = StagesUser.column_name
            text = 'Ваше сообщение сохранено, теперь введите название колонки с именами пользователей в excel файле.'
        case CallbackKeys.cancel_name:
            context.user_data[KeysStorage.stage] = StagesUser.column_name
            text = 'Введите название колонки снова!'
        case CallbackKeys.accept_name:
            context.user_data[KeysStorage.stage] = StagesUser.column_phone
            text = 'Ваше название колонки с именами пользователей сохранено, ' \
                   'теперь введите название колонки с номерами!'
        case CallbackKeys.cancel_phone:
            context.user_data[KeysStorage.stage] = StagesUser.column_phone
            text = 'Введите название колонки снова!'
        case CallbackKeys.accept_phone:
            context.user_data[KeysStorage.stage] = StagesUser.upload_file
            text = 'Ваше название колонки сохранено, теперь загрузите excel файл:3'
        case CallbackKeys.sending:
            context.user_data[KeysStorage.stage] = StagesUser.upload_file
            try:
                ud = UserData(**context.user_data)
                text = 'Начинаем рассылку сообщений!'
            except ValueError:
                logger.error('Bad validation for user data: {}'.format(context.user_data))
                await context.bot.send_message(
                    chat_id=q.message.chat_id,
                    message_id=q.message.message_id,
                    text='Произошла ошибка на сервере, попробуйте начать с начала:c'
                )
                return
            file_users = get_file(
                ud.file_path,
                ud.column_name,
                ud.column_phone
            )
            db_users = await cache.get_all_users()
            users = merge_users(db_users, file_users)
            await tfs_notify_task(context, users=users, message=ud.message)
        case CallbackKeys.cancel:
            text = 'Значит как только всё будет готово возвращайтесь к нам снова и начинайте сначала!'

        case CallbackKeys.create_admin:
            await context.bot.edit_message_text(
                update.effective_chat.id,
                text='Введите имя пользователя (он должен уже быть подписан на меня!)'
            )
            return
        case CallbackKeys.delete_admin:
            await context.bot.send_message(
                update.effective_chat.id,
                # todo: если нет пользователей для удаления надо выводить: некого понижать:D
                text='Выберите пользователя у которого хотите убрать права администратора:',
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(u.name, callback_data=u.name)
                            for u in await cache.get_all_users()
                            if u.name != update.effective_user.name.replace('@', '')
                        ]
                    ],
                ),
            )
            return
        case _:
            if choice in [u.name for u in admins]:
                u = await cache.get_user_by(name=choice, first=True)
                if u:
                    u.admin = False
                    await cache.update_user(u)
                    await context.bot.edit_message_text(
                        chat_id=q.message.chat_id,
                        message_id=q.message.message_id,
                        text='Пользователь {} лишен прав администратора!'.format(u.name),
                    )
                    return
                else:
                    logger.error('WTF with db and users')
            # default
            logger.error('Something wrong: stage: {}, user: {}, callback: {}'.format(stage, q.message.id, choice))
            text = 'Что-то произошло не так, попробуйте начать с начала:3'

    await context.bot.edit_message_text(
        chat_id=q.message.chat_id,
        message_id=q.message.message_id,
        text=text,
    )

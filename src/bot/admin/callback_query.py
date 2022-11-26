from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from dependency_injector.wiring import inject, Provide
from loguru import logger

from src.bot.admin.tasks import tfs_notify_task
from src.bot.admin.utils import get_file
from src.container import Container
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
            context.user_data[KeysStorage.stage] = StagesUser.mail
            text = 'Введите сообщение по новой!'
        case CallbackKeys.accept_msg:
            context.user_data[KeysStorage.stage] = StagesUser.choose_column_s
            text = 'Ваше сообщение сохранено, теперь введите название колонки с именами пользователей в excel файле:3'
        case CallbackKeys.cancel_name:
            context.user_data[KeysStorage.stage] = StagesUser.choose_column_s
            text = 'Введите название колонки снова!'
        case CallbackKeys.accept_name:
            context.user_data[KeysStorage.stage] = StagesUser.upload_file
            text = 'Ваше название колонки сохранено, теперь загрузите excel файл:3'
        case CallbackKeys.sending:
            context.user_data[KeysStorage.stage] = StagesUser.upload_file
            text = 'Начинаем рассылку сообщений!'

            # todo: лучше сделать доп проверку сверху на это всё по типу if k not in context.user_data: fail
            msg = context.user_data.get(KeysStorage.message, None)
            file_path = context.user_data.get(KeysStorage.file_path, None)
            column_name = context.user_data.get(KeysStorage.column_name, None)
            db_users = await cache.get_all_users()
            unames = {u.name: u.tg_id for u in db_users}
            subscribed = set(get_file(file_path, column_name)) & set(unames.keys())
            users = {user: unames[user] for user in subscribed}
            context.job_queue.run_once(tfs_notify_task, 1, users=users, message=msg)
        case CallbackKeys.cancel:
            text = 'Значит как только всё будет готово возвращайтесь к нам снова и начинайте сначала!'

        case CallbackKeys.create_admin:
            await context.bot.send_message(
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
                u.admin = False
                await cache.update_user(u)
                await context.bot.edit_message_text(
                    chat_id=q.message.chat_id,
                    message_id=q.message.message_id,
                    text='Пользователь {} лишен прав администратора!'.format(u.name),
                )
                return
            # default
            logger.error('Something wrong: stage: {}, user: {}, callback: {}'.format(stage, q.message.id, choice))
            text = 'Что-то произошло не так, попробуйте начать с начал:3'

    await context.bot.edit_message_text(
        chat_id=q.message.chat_id,
        message_id=q.message.message_id,
        text=text,
    )

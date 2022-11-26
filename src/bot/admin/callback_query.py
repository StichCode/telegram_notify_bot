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
    admins: list[int] = Provide[Container.config.provided.admin_users],
    cache: Cache = Provide[Container.cache]
) -> None:
    q = update.callback_query
    await q.answer()
    choice = q.data

    if update.effective_user.id not in admins:
        logger.info('User {} try to get admins route'.format(update.effective_user.name))
        return

    stage = context.user_data.get(KeysStorage.stage, None)
    if stage is None:
        logger.info('Something wrong with stage of user: {}'.format(stage))
        await context.bot.send_message(
            update.effective_user.id,
            text='Что то произошло на сервере, попробуйте начать сначала:c'
        )
        return

    if stage == StagesUser.writing:
        if choice == '0':
            context.user_data[KeysStorage.stage] = StagesUser.mail
            await context.bot.edit_message_text(
                chat_id=q.message.chat_id,
                message_id=q.message.message_id,
                text='Введите сообщение по новой!',
            )
            return
        elif choice == '1':
            context.user_data[KeysStorage.stage] = StagesUser.choose_column_s
            await context.bot.edit_message_text(
                chat_id=q.message.chat_id,
                message_id=q.message.message_id,
                text='Ваше сообщение сохранено, теперь введите название колонки с именами пользователей в excel файле:3',
            )
            return
    elif stage == StagesUser.choose_column_e:
        if choice == '0':
            context.user_data[KeysStorage.stage] = StagesUser.choose_column_s
            await context.bot.edit_message_text(
                chat_id=q.message.chat_id,
                message_id=q.message.message_id,
                text='Введите название колонки снова!',
            )
            return
        elif choice == '1':
            context.user_data[KeysStorage.stage] = StagesUser.upload_file
            await context.bot.edit_message_text(
                chat_id=q.message.chat_id,
                message_id=q.message.message_id,
                text='Ваше название колонки сохранено, теперь загрузите excel файл:3',
            )
            return

    elif stage == StagesUser.pre_send:
        if choice == '0':
            context.user_data[KeysStorage.stage] = None
            await context.bot.edit_message_text(
                chat_id=q.message.chat_id,
                message_id=q.message.message_id,
                text='Значит как только всё будет готово возвращайтесь к нам снова и начинайте сначала!',
            )
            return
        elif choice == '1':
            context.user_data[KeysStorage.stage] = StagesUser.upload_file

            # todo: лучше сделать доп проверку сверху на это всё по типу if k not in context.user_data: fail
            msg = context.user_data.get(KeysStorage.message, None)
            file_path = context.user_data.get(KeysStorage.file_path, None)
            column_name = context.user_data.get(KeysStorage.column_name, None)

            db_users = await cache.get_all_users()
            unames = {u.name: u.tg_id for u in db_users}
            subscribed = set(get_file(file_path, column_name)) & set(unames.keys())
            users = {user: unames[user] for user in subscribed}

            context.job_queue.run_once(tfs_notify_task, 1, users=users, message=msg)

            await context.bot.edit_message_text(
                chat_id=q.message.chat_id,
                message_id=q.message.message_id,
                text='Начинаем рассылку сообщений!',
            )

            return

    else:
        if choice == CallbackKeys.create_admin:
            await context.bot.send_message(
                update.effective_chat.id,
                text='Введите имя пользователя (он должен уже быть подписан на меня!',
            )
        elif choice == CallbackKeys.delete_admin:
            pass

    logger.error('Something wrong: stage: {}, user: {}, callback: {}'.format(stage, q.message.id, choice))
    await context.bot.send_message(
        update.effective_user.id,
        text='Что то произошло на сервере, попробуйте начать сначала:c'
    )

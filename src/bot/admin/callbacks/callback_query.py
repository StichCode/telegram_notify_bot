from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from dependency_injector.wiring import inject, Provide
from loguru import logger

from src.bot.admin.functions.chose_coolumns import choose_columns
from src.bot.admin.tasks import tfs_notify_task
from src.bot.admin.utils import get_file, merge_users, to_sublist
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
    if '_' in choice:
        return await choose_columns(context=context, choice=choice, callback_query=q, cache=cache)

    match choice:
        case CallbackKeys.cancel_msg:
            context.user_data[KeysStorage.stage] = StagesUser.create_message
            text = 'Введите сообщение по новой!'
        case CallbackKeys.accept_msg:
            context.user_data[KeysStorage.stage] = StagesUser.upload_file
            text = 'Теперь загрузите ваш xlsx файл 🧡'
        case CallbackKeys.sending:
            context.user_data[KeysStorage.stage] = StagesUser.upload_file
            ud = UserData(**context.user_data)
            users, _ = get_file(ud)
            users = merge_users(await cache.get_all_users(), users)
            sends = await tfs_notify_task(
                context,
                users=users,
                message=ud.message
            )
            text = 'Сообщения разосланы: {}/{}'.format(sends, len(users))
        case CallbackKeys.cancel:
            text = 'Значит как только всё будет готово возвращайтесь к нам снова и начинайте сначала!'
        case CallbackKeys.create_admin:

            await context.bot.edit_message_text(
                chat_id=q.message.chat_id,
                message_id=q.message.message_id,
                text='Введите имя пользователя (он должен уже быть подписан на меня!)'
            )
            return
        case CallbackKeys.delete_admin:
            text = 'Выберите пользователя у которого хотите убрать права администратора:'
            cur_username = update.effective_user.name.replace('@', '')
            btns = to_sublist(
                [
                    InlineKeyboardButton(u.name, callback_data=u.name)
                    for u in await cache.get_all_users(only_admins=True) if u.name != cur_username
                ]
            )
            keyboard = InlineKeyboardMarkup(inline_keyboard=btns)
            if not btns:
                text = 'Нет пользователей которых можно понизить:D'
                keyboard = None
            await context.bot.edit_message_text(
                chat_id=q.message.chat_id,
                message_id=q.message.message_id,
                text=text,
                reply_markup=keyboard,
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

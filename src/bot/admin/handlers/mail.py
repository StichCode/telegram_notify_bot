from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from dependency_injector.wiring import inject, Provide

from loguru import logger

from src.container import Container
from src.storage.cache import Cache
from src.storage.enums import KeysStorage, StagesUser


@inject
async def mail_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    cache: Cache = Provide[Container.cache]
) -> None:
    """
    Workflow sender:
        1. Ввод сообщения для рассылки
        2. Загрузка excel файла
        3. Выбор колонки с именами пользователей
        4. Выбор колонки с номерами телефонов
        5. Проверка пользователей и файла
        6. Подтверждение и после рассылка писем

    :param update:
    :param context:
    :param cache:
    :return:
    """
    if not await cache.is_admin(update.effective_user.id):
        logger.info('User {} try to get admins route'.format(update.effective_user.name))
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Перед началом рассылки введите сообщение для рассылки:',
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data[KeysStorage.stage] = StagesUser.create_message

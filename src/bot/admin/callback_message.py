from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from dependency_injector.wiring import inject, Provide
from loguru import logger

from src.container import Container
from src.storage.enums import KeysStorage, StagesUser


@inject
async def callback_message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    admins: list[int] = Provide[Container.config.provided.admin_users]
) -> None:
    if update.effective_user.id not in admins:
        logger.info('User {} try to get admins route'.format(update.effective_user.name))
        return

    # проверяем что стейдж пользователя позволяет сохранить сообщение
    stage = context.user_data.get(KeysStorage.stage, None)
    if stage is None:
        logger.info('Something wrong with stage of user: {}'.format(stage))
        await context.bot.send_message(
            update.effective_user.id,
            text='Что то произошло на сервере, попробуйте начать сначала:c'
        )
        return
    if stage == StagesUser.mail:
        context.user_data[KeysStorage.stage] = StagesUser.writing
        context.user_data[KeysStorage.message] = update.message.text
        await context.bot.send_message(
            update.effective_user.id,
            text='Вы уверены что хотите разослать это сообщение:\n\n{}'.format(update.message.text),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton("Да", callback_data='1'),
                        InlineKeyboardButton("Нет", callback_data='0')
                    ]
                ],
            ),
        )
    elif stage == StagesUser.choose_column_s:
        context.user_data[KeysStorage.stage] = StagesUser.choose_column_e
        context.user_data[KeysStorage.column_name] = update.message.text
        await context.bot.send_message(
            update.effective_user.id,
            text='Вы уверены что ввели верное название колонки?:\n{}'.format(update.message.text),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton("Да", callback_data='1'),
                        InlineKeyboardButton("Нет", callback_data='0')
                    ]
                ],
            ),
        )

    elif stage == StagesUser.administration:
        # todo: найти юзера в кэше и если он там есть, то добавить в админов
        await context.bot.send_message(
            update.effective_user.id,
            text='Пользователь {} успешно повышен до администратора!'.format(update.message.text),
        )



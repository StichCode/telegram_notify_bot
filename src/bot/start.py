from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from dependency_injector.wiring import inject, Provide

from loguru import logger

from src.container import Container
from src.dto.user import User
from src.storage.cache import Cache


@inject
async def start_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    cache: Cache = Provide[Container.cache],
    default_admins: list[int] = Provide[Container.config.provided.default_admins]
) -> None:
    """
    Start message for users
    :param default_admins:
    :param cache:
    :param update:
    :param context:
    :return:
    """
    user = User(
        tg_id=update.effective_user.id,
        name=update.effective_user.name,
        admin=update.effective_user.id in default_admins
    )
    u = await cache.get_user_by(user.tg_id, user.name, first=True)
    if u:
        msg = 'Вы уже подписаны на нашу рассылку, как только мы будем готовы ' \
              'мы вам напишем!'
        footer = '\n\nС любовью @trip_for_students 🧡'
        if not u.phone:
            msg += '\nНо у нас всё ещё нет вашего телефона,\n' \
                   'нам будет затруднительно найти вас для рассылки вовремя,\n' \
                   'пожалуйста поделитесь с нами телефоном!:3\n\nДля этого нажмите на кнопку!'
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=str(msg + footer),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton('Поделится телефоном', request_contact=True),
                    ],
                ],
                resize_keyboard=True,
                one_time_keyboard=True,
            ) if not u.phone else None
        )
        return

    _ = await cache.save_user(user)
    logger.info('Save new user: {}'.format(user))

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Спасибо что подписались на нас!\n'
             'Предоставьте так же нам информацию о своем номере телефона, '
             'что бы мы могли найти вас в наших списках:3\n\n'
             'С любовью @trip_for_students 🧡',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton('Поделится телефоном', request_contact=True),
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    )

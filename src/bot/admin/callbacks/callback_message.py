from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from dependency_injector.wiring import inject, Provide
from loguru import logger

from src.container import Container
from src.storage.cache import Cache
from src.storage.enums import KeysStorage, StagesUser, CallbackKeys


@inject
async def callback_message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    cache: Cache = Provide[Container.cache]
) -> None:
    if not await cache.is_admin(update.effective_user.id):
        logger.info('User {} try to get admins route'.format(update.effective_user.name))
        logger.debug("User: {}, send: {}".format(update.effective_user.id, update.message.text))
        return
    btns = None
    # проверяем что стейдж пользователя позволяет сохранить сообщение
    stage = context.user_data.get(KeysStorage.stage, None)
    if stage is None:
        logger.info('Something wrong with stage of user: {}'.format(stage))
        await context.bot.send_message(
            update.effective_user.id,
            text='Что то произошло на сервере, попробуйте начать сначала:c'
        )
        return

    match stage:
        case StagesUser.create_message:
            context.user_data[KeysStorage.message] = update.message.text
            text = 'Вы уверены что хотите разослать это сообщение:\n\n{}'.format(update.message.text)
            btns = [
                InlineKeyboardButton("Да", callback_data=CallbackKeys.accept_msg),
                InlineKeyboardButton("Нет", callback_data=CallbackKeys.cancel_msg)
            ]
        case StagesUser.administration:
            u = await cache.get_user_by(name=update.message.text, first=True)
            if not u:
                text = 'Нет пользователя под именем {}, который был бы на меня подписан'.format(update.message.text)
            else:
                text = 'Пользователь {} успешно повышен до администратора!'.format(update.message.text)
            u.admin = True
            await cache.update_user(u)
        case _:
            logger.error('Something strange happens with stage: `{}`'.format(stage))
            return

    await context.bot.send_message(
        update.effective_user.id,
        text=text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[btns]
        ) if btns else None,
    )

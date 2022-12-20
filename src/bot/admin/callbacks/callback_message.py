from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from dependency_injector.wiring import inject, Provide
from loguru import logger

from config.messages import Messages
from src.container import Container
from src.storage.cache import Cache
from src.storage.enums import KeysStorage, StagesUser, CallbackKeys


@inject
async def callback_message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    cache: Cache = Provide[Container.cache],
    msgs: Messages = Provide[Container.messages]
) -> None:
    if not await cache.is_admin(update.effective_user.id):
        logger.debug("User: {}, send: {}".format(update.effective_user.id, update.message.text))
        return
    btns = None
    # проверяем что стейдж пользователя позволяет сохранить сообщение
    stage = context.user_data.get(KeysStorage.stage, None)
    if stage is None:
        logger.info('Something wrong with stage of user: {}'.format(stage))
        await context.bot.send_message(
            update.effective_user.id,
            text=msgs.default_msg.stage_fail
        )
        return

    match stage:
        case StagesUser.create_message:
            context.user_data[KeysStorage.message] = update.message.text
            text = msgs.mail.verify_msg.format(update.message.text)
            btns = [
                InlineKeyboardButton(msgs.buttons.default_yes, callback_data=CallbackKeys.accept_msg),
                InlineKeyboardButton(msgs.buttons.default_no, callback_data=CallbackKeys.cancel_msg)
            ]
        case StagesUser.administration:
            u = await cache.get_user_by(name=update.message.text.strip(), first=True)
            if u:
                text = msgs.admins.fail_not_subscribe if not u else msgs.admins.success
                text = text.format(u.name)
                u.admin = True
                await cache.update_user(u)
            else:
                logger.debug('fail for update admin')
                text = 'Что то пошло не так:c'
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

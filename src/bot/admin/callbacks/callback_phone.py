from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from dependency_injector.wiring import inject, Provide

from src.container import Container
from src.storage.cache import Cache


@inject
async def callback_phone_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    cache: Cache = Provide[Container.cache]
) -> None:
    u = await cache.get_user_by(tg_id=update.effective_user.id, name=update.effective_user.name, first=True)
    if u and not u.phone:
        u.phone = update.message.contact.phone_number
        await cache.update_user(u)
        await context.bot.send_message(
            update.effective_chat.id,
            text='Спасибо мы сохранили ваш номер 🧡',
            reply_markup=ReplyKeyboardRemove()
        )


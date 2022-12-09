from telegram import Update
from telegram.ext import ContextTypes


async def tours_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Мы пока делаем эту функцию, но скоро всё будет готово 🧡'
    )

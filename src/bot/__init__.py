from typing import Any

from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters

from src.bot.admin.callback_file import callback_file_handler
from src.bot.admin.callback_message import callback_message_handler
from src.bot.admin.callback_phone import callback_phone_handler
from src.bot.admin.callback_query import callback_query_handler
from src.bot.admin.mail import mail_handler
from src.bot.help import help_handler
from src.bot.start import start_handler


def get_handlers() -> list[CommandHandler[CallbackContext | Any]]:
    # ToDo: add handler to set timezone
    return [
        CommandHandler('start', start_handler),
        CommandHandler('help', help_handler),
        CommandHandler('mail', mail_handler),
        MessageHandler(filters.Document.ALL, callback=callback_file_handler),
        MessageHandler(filters.CONTACT, callback=callback_phone_handler),
        MessageHandler(filters.TEXT & (~filters.COMMAND), callback_message_handler),
        CallbackQueryHandler(callback_query_handler)
    ]

from typing import Any

from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters

from src.bot.admin.handlers.admins import admins_handler
from src.bot.admin.callbacks.callback_file import callback_file_handler
from src.bot.admin.callbacks.callback_message import callback_message_handler
from src.bot.admin.callbacks.callback_phone import callback_phone_handler
from src.bot.admin.callbacks.callback_query import callback_query_handler
from src.bot.admin.handlers.mail import mail_handler
# from src.bot.admin.handlers.users import users_handler
from src.bot.help import help_handler
from src.bot.start import start_handler
from src.bot.tours import tours_handler


def get_handlers() -> list[CommandHandler[CallbackContext | Any]]:
    return [
        CommandHandler('start', start_handler),
        CommandHandler('help', help_handler),
        CommandHandler('mail', mail_handler),
        # CommandHandler('users', users_handler),
        CommandHandler('admins', admins_handler),
        CommandHandler('tours', tours_handler),
        MessageHandler(filters.Document.ALL, callback=callback_file_handler),
        MessageHandler(filters.CONTACT, callback=callback_phone_handler),
        MessageHandler(filters.TEXT & (~filters.COMMAND), callback_message_handler),
        CallbackQueryHandler(callback_query_handler)
    ]

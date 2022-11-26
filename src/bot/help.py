from dependency_injector.wiring import inject, Provide

from telegram import Update
from telegram.ext import ContextTypes

from src.container import Container


@inject
async def help_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    admins: list[int] = Provide[Container.config.provided.admin_users]
) -> None:
    text = "Команды доступны вам для использования:\n"

    commands = [
        ["/start", "Зарегистрироваться для получения уведомлений о ваших путешествиях {}".format(
            update.effective_user.name
        )],
    ]
    if update.effective_user.id in admins:
        commands = [
                ["/mail", "Создает новую рассылку сообщений по пользователям"],
                ["/users", "Получение пользователей подписанных на рассылку"],
                ["/admins", "Изменить администраторов"],
                ["/help", "Возвращает это сообщение"]
            ]
    for command in commands:
        text += "{0:8s} - {1:10s}\n".format(command[0], command[1])

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

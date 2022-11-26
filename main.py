import sys
from loguru import logger

import pytz
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, Application, Defaults

from src.bot import get_handlers
from src.container import Container


class App:

    def __init__(self):
        self._container = Container()
        self.__init_container()
        self._app = self._init_app()

    def __init_container(self) -> None:
        self._container.wire(
            modules=[
                sys.modules[__name__],
                sys.modules["src.bot.help"],
                sys.modules["src.bot.start"],
                sys.modules["src.bot.admin.mail"],
                sys.modules["src.bot.admin.callback_file"],
                sys.modules["src.bot.admin.callback_message"],
                sys.modules["src.bot.admin.callback_query"],
                sys.modules["src.bot.admin.callback_phone"],
                sys.modules["src.bot.admin.admins"],

            ]
        )
        self._container.init_resources()

    def _init_app(self) -> Application:
        defaults = Defaults(parse_mode=ParseMode.HTML, tzinfo=pytz.timezone('Europe/Moscow'))

        _app = ApplicationBuilder().token(self._container.config().tg_token).defaults(defaults).build()
        _app.add_handlers(get_handlers())

        return _app

    def run(self) -> None:
        logger.info('bot has been started :3')
        self._app.run_polling()


if __name__ == '__main__':
    app = App()
    app.run()

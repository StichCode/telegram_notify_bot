import sys

import sentry_sdk
from loguru import logger

import pytz
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, Application, Defaults, JobQueue

from src.bot import get_handlers
from src.bot.admin.tasks import create_db
from src.container import Container


class App:

    def __init__(self) -> None:
        self._container = Container()
        self.__init_container()
        self._app = self._init_app()
        self.__init_tracers()

    def __init_tracers(self) -> None:
        sentry_sdk.init(
            dsn=self._container.config().sentry_dsn,
            traces_sample_rate=1.0,
        )

    def __init_container(self) -> None:
        self._container.wire(
            modules=[
                sys.modules[__name__],
                sys.modules["src.bot.help"],
                sys.modules["src.bot.start"],
                sys.modules["src.bot.admin.handlers.mail"],
                sys.modules["src.bot.admin.handlers.users"],
                sys.modules["src.bot.admin.callbacks.callback_file"],
                sys.modules["src.bot.admin.callbacks.callback_message"],
                sys.modules["src.bot.admin.callbacks.callback_query"],
                sys.modules["src.bot.admin.callbacks.callback_phone"],
                sys.modules["src.bot.admin.handlers.admins"],
                sys.modules["src.bot.admin.functions.verification_xlsx_file"],
            ]
        )
        self._container.init_resources()

    def _init_app(self) -> Application:
        defaults = Defaults(parse_mode=ParseMode.HTML, tzinfo=pytz.timezone('Europe/Moscow'))

        _app: Application = ApplicationBuilder().token(self._container.config().tg_token).defaults(defaults).build()
        _app.add_handlers(get_handlers())
        jq = _app.job_queue
        jq.run_once(create_db, when=0.1, name='init_db')

        return _app

    def run(self) -> None:
        logger.info('bot has been started :3')
        self._app.run_polling()


if __name__ == '__main__':
    app = App()
    app.run()

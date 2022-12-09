from dependency_injector import containers, providers

from config.config import Configuration
from config.messages import Messages
from src.storage.cache import Cache
from src.storage.simple_cache import MeowCache

from src.storage.sql_transport import SQLTransport


class Container(containers.DeclarativeContainer):
    config: providers.Singleton[Configuration] = providers.Singleton(Configuration)
    meow: providers.Singleton[MeowCache] = providers.Singleton(MeowCache)
    messages: providers.Singleton[Messages] = providers.Singleton(Messages)

    _sql: providers.Singleton[SQLTransport] = providers.Singleton(
        SQLTransport,
        cfg=config.provided
    )

    cache: providers.Factory[Cache] = providers.Factory(
        Cache,
        transport=_sql
    )

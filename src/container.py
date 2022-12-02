from dependency_injector import containers, providers

from src.config import Configuration
from src.storage.cache import Cache

from src.storage.sql_transport import SQLTransport


class Container(containers.DeclarativeContainer):
    config: providers.Singleton[Configuration] = providers.Singleton(Configuration)

    _sql: providers.Singleton[SQLTransport] = providers.Singleton(
        SQLTransport,
        cfg=config.provided
    )

    cache: providers.Factory[Cache] = providers.Factory(
        Cache,
        transport=_sql
    )

from typing import Any

from pydantic.class_validators import root_validator
from pydantic.env_settings import BaseSettings
from pydantic.fields import Field


class _BS(BaseSettings):
    class Config:
        env_file = '.env'


class PostgresConfig(_BS):
    host: str = Field(env='PG_HOST')
    port: int = Field(env='PG_PORT')
    db: str = Field(env='PG_DB')
    schema_db: str = Field(env='PG_SCHEMA')
    user: str = Field(env='PG_USER')
    password: str = Field(env='PG_PASSWORD')


class Configuration(_BS):
    tg_token: str = Field(env='TG_TOKEN')
    default_admins: list[int] = Field(env='ADMIN_USERS')
    sentry_dsn: str = Field('SENTRY_DSN')

    pg: PostgresConfig

    @root_validator(pre=True)
    def _better_init_fabrics(cls, values: dict[str, Any]) -> dict[str, Any]:
        if 'pg' not in values:
            values['pg'] = PostgresConfig()
        return values

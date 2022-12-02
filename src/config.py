from pydantic.env_settings import BaseSettings
from pydantic.fields import Field


class Configuration(BaseSettings):
    tg_token: str = Field(env='TG_TOKEN')
    default_admins: list[int] = Field(env='ADMIN_USERS')

    user: str = Field(env='PG_USER')
    password: str = Field(env='PG_PASSWORD')
    db: str = Field(env='PG_DB')
    schema_db: str = Field(env='PG_SCHEMA')
    host: str = Field(env='PG_HOST')
    port: int = Field(env='PG_PORT')

    class Config:
        env_file = '.env'


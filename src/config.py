from pydantic.env_settings import BaseSettings
from pydantic.fields import Field


class Configuration(BaseSettings):
    tg_token: str = Field(env='TG_TOKEN')
    default_admins: list[int] = Field(env='ADMIN_USERS')

    class Config:
        env_file = '.env'


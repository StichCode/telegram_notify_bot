from pydantic.env_settings import BaseSettings
from pydantic.fields import Field


class _BS(BaseSettings):
    class Config:
        env_file = '.env'


class GoogleExcelConfig(_BS):
    const_columns: list[str] = ['month', 'num', 'name', 'count', 'total']
    sheet_id: str = Field(env='GOOGLE_SHEET_ID')
    range_name: str = Field(env='GOOGLE_RANGE_NAME')  # like: Sheet!A2:E50
    credentials: str = Field(env='GOOGLE_CREDS')
    scopes: list[str] = ['https://www.googleapis.com/auth/spreadsheets.readonly']


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

    pg: PostgresConfig = Field(default_factory=PostgresConfig)
    google_cfg: GoogleExcelConfig = Field(default_factory=GoogleExcelConfig)

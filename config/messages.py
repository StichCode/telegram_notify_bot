from typing import Any

from pydantic.class_validators import validator
from pydantic.env_settings import SettingsSourceCallable, BaseSettings
from pydantic.main import BaseModel

from src.bot.admin.utils import to_sublist
from config.core.yaml_source import yaml_settings


class _BM(BaseModel):
    @validator('*')
    def replace(cls, v: Any) -> str | None:
        if isinstance(v, str):
            return v.replace("\\n", "\n")
        return v


class Start(_BM):
    first: str
    if_exist: str
    if_exist_without_phone: str
    complete_save: str


class Help(_BM):
    message: str
    user: dict[str, str]
    admin: dict[str, str]

    @validator('user', 'admin', pre=True)
    def filling_data(cls, v: list[str]) -> dict[str, str]:
        if v:
            return {d[0]: d[1] for d in to_sublist(v, sep=2)}


class Users(_BM):
    columns: list[str]
    message: str


class Admins(_BM):
    first: str
    create_admin: str
    delete_admin: str
    no_users: str
    fail_not_subscribe: str
    take_away_admin: str
    success: str


class Mail(_BM):
    first: str
    verify_msg: str
    cancel_msg: str
    accept_msg: str
    bad_format_file: str
    xlsx_column_fail: str
    choose_column_name: str
    bad_data: str
    not_subs: str
    not_subs_all: str
    pre_send_msg: str
    error_msg: str
    final_msg: str


class DefaultMsg(_BM):
    stage_fail: str


class Buttons(_BM):
    send_phone: str
    add_admin: str
    delete_admin: str

    default_yes: str
    default_no: str


class Messages(BaseSettings):
    start: Start
    help: Help
    users: Users
    admins: Admins
    mail: Mail
    default_msg: DefaultMsg
    buttons: Buttons

    class Config:
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> tuple[SettingsSourceCallable, ...]:
            return yaml_settings, init_settings

import re

from pydantic.class_validators import validator
from pydantic.main import BaseModel


class User(BaseModel):
    tg_id: int
    name: str = ''
    phone: str | None = ''
    admin: bool = False

    @validator('name', pre=True)
    def check_name(cls, v: str) -> str | None:
        if '@' in v:
            v = v.replace('@', '')
        if v and bool(re.search('[а-яА-Я]', v)):
            return ''
        return v

    @validator('phone')
    def check_phone(cls, v: str) -> str:
        # fixme: if number like (+7/7/8) 7... - regular exception not see this number
        regex = r"^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$"
        if v:
            v = v.strip().replace(' ', '')
        if v and not re.search(regex, v, re.I):
            return None
        v = v.replace('-', '').replace('(', '').replace(')', '')
        s = re.search(r"^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?", v).group()
        if 4 <= len(s) <= 5:
            v = v.replace(s, "8{}".format(s[-3:]))
        return v

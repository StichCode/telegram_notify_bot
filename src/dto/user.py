import re

from pydantic.class_validators import validator
from pydantic.main import BaseModel
from loguru import logger

from src.errors import BadPhoneNumber


class User(BaseModel):
    tg_id: int
    name: str | None = None
    phone: str | None = ''
    admin: bool = False

    def __str__(self) -> str:
        return "{0} {1} {2}".format(self.tg_id, self.name, self.phone)

    @validator('name', pre=True)
    def check_name(cls, v: str) -> str | None:
        if '@' in v:
            v = v.replace('@', '')
        if v and bool(re.search('[а-яА-Я]', v)):
            return ''
        return v

    @validator('phone')
    def check_phone(cls, v: str) -> str:
        regex = "^\\+?\\d{1,4}?[-.\\s]?\\(?\\d{1,3}?\\)?[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,9}$"
        if not v:
            return ''
        v = v.strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        v = re.search(regex, v).group()
        if not v:
            raise BadPhoneNumber
        if v[0] == '+':
            v = v[1:]
        elif v[0] == '8':
            v = '7{}'.format(v[1:])
        elif v[0] == '7':
            pass
        else:
            logger.warning('Unknown number: {}'.format(v))
        return v

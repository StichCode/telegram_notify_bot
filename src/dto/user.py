from pydantic.main import BaseModel


class User(BaseModel):
    tg_id: int
    name: str | None

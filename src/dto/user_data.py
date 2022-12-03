from pydantic.main import BaseModel


class UserData(BaseModel):
    stage: str
    message: str
    column_phone: str
    file_path: str

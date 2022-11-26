from src.dto.user import User
from src.storage.sql_transport import SQLTransport


class Cache:
    def __init__(self, transport: SQLTransport) -> None:
        self._tr = transport

    async def init_db(self) -> None:
        await self._tr.create_db()

    async def is_admin(self, tg_id: int) -> bool:
        user = await self._tr.get_user_by_(tg_id=tg_id, first=True)
        return user.admin

    async def update_user(self, user: User) -> None:
        await self._tr.update_user(user)

    async def get_all_users(self) -> list[User]:
        return await self._tr.get_all_users()

    async def get_user_by(
        self,
        tg_id: int | None = None,
        name: str | None = None,
        first: bool = False
    ) -> list[User] | User:
        return await self._tr.get_user_by_(tg_id=tg_id, name=name, first=first)

    async def save_user(self, user: User) -> None:
        await self._tr.save_user(user)

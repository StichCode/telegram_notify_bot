import os.path
from pathlib import Path
from loguru import logger

import aiosqlite

from src.dto.user import User


class SQLTransport:
    file_name: str = 'db.sqlite'

    def __init__(self) -> None:
        self.path = Path(os.path.dirname(__file__), '..', '..', self.file_name)

    # todo: init db
    async def create_db(self) -> None:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute("""
                CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER NOT NULL UNIQUE,
                name TEXT NOT NULL UNIQUE,
                admin BOOLEAN NOT NULL,
                phone TEXT
                )
            """)

    async def get_all_users(self, *, only_admins: bool = False) -> list[User]:
        users = []
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            sql = 'select * from user'
            if only_admins:
                sql += ' where admin = true;'
            async with db.execute(sql) as cursor:
                async for row in cursor:
                    users.append(User(**row))
        return users

    async def update_user(self, u: User) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("UPDATE user SET admin=?, phone=? WHERE tg_id = ?", [u.admin, u.phone, u.tg_id])
            await db.commit()
            logger.info('User something update')

    async def get_user_by_(
        self,
        *,
        tg_id: str | None = None,
        name: str | None = None,
        first: bool = False
    ) -> list[User] | User | None:
        users = []
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('select * from user where tg_id = ? OR name = ?;', [tg_id, name]) as cursor:
                async for row in cursor:
                    users.append(User(**row))
        if first:
            # fixme: fucking dirty hacks
            if users:
                return users[0]
            else:
                return None
        return users

    async def save_user(self, user: User) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT INTO user (tg_id, name, admin) VALUES (?, ?, ?)",
                [user.tg_id, user.name, user.admin]
            )
            await db.commit()
            logger.debug(f'saved user: {user}')

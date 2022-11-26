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
                tg_id INTEGER NOT NULL ,
                name TEXT NOT NULL
                )
            """)

    async def get_all_users(self) -> list[User]:
        users = []
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('select * from user;') as cursor:
                async for row in cursor:
                    users.append(User(**row))
        return users

    async def get_user_by_(self, tg_id: str | None, name: str | None) -> list[User]:
        users = []
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('select * from user where tg_id = ? OR name = ?;', [tg_id, name]) as cursor:
                async for row in cursor:
                    users.append(User(**row))
        return users

    async def save_user(self, user: User) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("INSERT INTO user (tg_id, name) VALUES (?, ?)", [user.tg_id, user.name])
            await db.commit()
            logger.info('saved user')

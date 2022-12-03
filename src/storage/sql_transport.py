import asyncpg
from asyncpg.connection import Connection

from loguru import logger

from src.config.config import Configuration
from src.dto.user import User


class SQLTransport:
    # todo: use ORM

    def __init__(self, cfg: Configuration) -> None:
        self.cfg = cfg.pg

    async def conn(self) -> Connection:
        # todo: create context
        return await asyncpg.connect(
            user=self.cfg.user, password=self.cfg.password,
            database=self.cfg.db, host=self.cfg.host, port=self.cfg.port
        )

    async def create_db(self) -> None:
        conn = await self.conn()
        cur = await conn.execute("""
            CREATE TABLE IF NOT EXISTS {}.user (
            id SERIAL PRIMARY KEY,
            tg_id INTEGER NOT NULL UNIQUE,
            name TEXT NOT NULL UNIQUE,
            admin BOOLEAN NOT NULL,
            phone TEXT
            )
        """.format(self.cfg.schema_db))

    async def get_all_users(self, *, only_admins: bool = False) -> list[User]:
        users = []
        conn = await self.conn()
        sql = 'select * from {}.user'.format(self.cfg.schema_db)
        if only_admins:
            sql += ' where admin = true;'
        db_users = await conn.fetch(sql)
        users.extend([User(**row) for row in db_users])
        return users

    async def update_user(self, u: User) -> None:
        conn = await self.conn()
        await conn.execute(
            "UPDATE {}.user SET admin=$1, phone=$2 WHERE tg_id = $3".format(self.cfg.schema_db),
            u.admin, u.phone, u.tg_id
        )
        logger.info('User something update')

    async def get_user_by_(
        self,
        *,
        tg_id: str | None = None,
        name: str | None = None,
        first: bool = False
    ) -> list[User] | User | None:
        if name is None and tg_id is None:
            # raise bad args
            return None
        users = []
        conn = await self.conn()
        db_users = await conn.fetch(
            'select * from {}.user where tg_id = $1 OR name = $2'.format(self.cfg.schema_db),
            tg_id, name
        )
        users.extend([User(**row) for row in db_users])
        # todo: dirty hack need another method
        if users and first:
            return users[0]
        if not users and first:
            return None
        return users

    async def save_user(self, user: User) -> None:
        conn = await self.conn()
        sql = 'INSERT INTO {}.user (tg_id, name, admin) ' \
              'VALUES'.format(self.cfg.schema_db) + " ($1, $2, $3)"
        await conn.execute(
            sql,
            user.tg_id, user.name, user.admin)
        logger.debug(f'saved user: {user}')

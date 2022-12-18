import asyncpg
import asyncio

from utils.db_api.db import Database
from utils.db_api.users_models import User, Users


class UsersDB(Database):
    def __init__(self):
        super().__init__()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.create_tables())

    async def create_tables(self):
        sql = """
        CREATE TABLE IF NOT EXISTS type_users_list (
            id SERIAL PRIMARY KEY,
            name text UNIQUE 
        );

        CREATE TABLE IF NOT EXISTS users (
            telegram_id bigint NOT NULL UNIQUE PRIMARY KEY,
            full_name character varying(255) NOT NULL,
            username character varying(255),
            phone character varying(255) UNIQUE default NULL,
            type_user_id integer REFERENCES type_users_list(id) DEFAULT 1,
            time_created timestamp DEFAULT now()
        );
        """
        await self._execute(sql, execute=True)

    # Пользователи
    async def _format_user(self, record: asyncpg.Record) -> User:
        return User(
            telegram_id=record['telegram_id'],
            full_name=record['full_name'],
            username=record['username'],
            phone=record['phone'],
            type=(await self.select_user_type_dy_id(record['type_user_id']))
        )

    async def add_user(self, full_name: str, username: str, telegram_id: int) -> User:
        """
        Добавление пользователя в базу данных

        :param full_name: user's fullname from telegram
        :param username: user's username from telegram
        :param telegram_id: user's id from telegram
        :return:
        """
        sql = "INSERT INTO users (full_name, username, telegram_id) VALUES($1, $2, $3) returning *"
        record = await self._execute(sql, full_name, username, telegram_id, fetchrow=True)
        return await self._format_user(record)

    async def update_user_fullname(self, full_name: str, telegram_id: int):
        sql = "UPDATE users SET full_name=$1 WHERE telegram_id=$2"
        return await self._execute(sql, full_name, telegram_id, execute=True)

    async def update_user_username(self, username: str, telegram_id: int):
        sql = "UPDATE users SET username=$1 WHERE telegram_id=$2"
        return await self._execute(sql, username, telegram_id, execute=True)

    async def update_user_phone(self, phone: str, telegram_id: int):
        sql = "UPDATE users SET phone=$1 WHERE telegram_id=$2"
        return await self._execute(sql, phone, telegram_id, execute=True)

    async def select_all_users(self) -> Users:
        sql = "SELECT * FROM users ORDER BY type_user_id DESC"
        list_of_records = await self._execute(sql, fetch=True)
        return Users([await self._format_user(record) for record in list_of_records])

    # async def select_user(self, **kwargs) -> asyncpg.Record:
    #     sql = "SELECT * FROM users WHERE "
    #     sql, parameters = self.format_args(sql, parameters=kwargs)
    #     return await self.execute(sql, *parameters, fetchrow=True)

    async def select_user(self, telegram_id: int) -> User:
        sql = "SELECT * FROM users WHERE telegram_id=$1"
        record = await self._execute(sql, telegram_id, fetchrow=True)
        return await self._format_user(record)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM users"
        return await self._execute(sql, fetchval=True)

    async def delete_user(self, telegram_id):
        await self._execute("DELETE FROM users WHERE telegram_id=$1", telegram_id, execute=True)

    async def delete_users(self):
        await self._execute("DELETE FROM users WHERE TRUE", execute=True)

    async def drop_users(self):
        await self._execute("DROP TABLE IF EXISTS users CASCADE ", execute=True)

    # Типы пользователей
    async def add_user_type(self, name: str) -> asyncpg.Record:
        sql = "INSERT INTO type_users_list (name) VALUES($1) returning *"
        return await self._execute(sql, name, fetchrow=True)

    async def select_user_type(self, user_type: str) -> int:
        sql = "SELECT id FROM type_users_list WHERE name=$1"
        return await self._execute(sql, user_type, fetchval=True)

    async def select_user_type_dy_id(self, id: int) -> str:
        sql = "SELECT name FROM type_users_list WHERE id=$1"
        return await self._execute(sql, id, fetchval=True)

    async def select_all_user_types(self) -> list[asyncpg.Record]:
        sql = "SELECT * FROM type_users_list"
        return await self._execute(sql, fetch=True)

    async def select_users_by_type(self, type_user_id: int) -> Users:
        sql = "SELECT * FROM users WHERE type_user_id=$1"
        list_of_records = await self._execute(sql, type_user_id, fetch=True)
        return Users([await self._format_user(record) for record in list_of_records])

    async def update_user_type(self, new_type: int, telegram_id: int) -> asyncpg.Record:
        sql = "UPDATE users SET type_user_id=$1 WHERE telegram_id=$2"
        return await self._execute(sql, new_type, telegram_id, execute=True)

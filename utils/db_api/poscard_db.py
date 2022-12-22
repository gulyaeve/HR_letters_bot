import asyncio
import datetime
from dataclasses import dataclass

import asyncpg

from utils.db_api.db import Database


@dataclass
class Postcard:
    id: int
    user_id_who_sent: int
    user_id_to_sent: int
    file_id: str
    raw_file: bytes
    time_created: datetime.datetime
    time_sended_telegram: datetime.datetime | None
    time_sended_email: datetime.datetime | None


class PostcardsDB(Database):
    def __init__(self):
        super().__init__()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.create_tables())

    async def create_tables(self):
        sql = """
        CREATE TABLE IF NOT EXISTS postcards (
            id SERIAL PRIMARY KEY,
            user_id_who_sent bigint,
            user_id_to_sent bigint,
            file_id text,
            raw_file bytea,
            time_created timestamp DEFAULT now(),
            time_sended_telegram timestamp DEFAULT NULL,
            time_sended_email timestamp DEFAULT NULL
        );
        """
        await self._execute(sql, execute=True)

    @staticmethod
    async def _format_postcard(record: asyncpg.Record) -> Postcard:
        return Postcard(
            id=record['id'],
            user_id_who_sent=record['user_id_who_sent'],
            user_id_to_sent=record['user_id_to_sent'],
            file_id=record['file_id'],
            raw_file=record['raw_file'],
            time_created=record['time_created'],
            time_sended_telegram=record['time_sended_telegram'],
            time_sended_email=record['time_sended_email'],
        )

    async def insert_postcard(self, user_id_who_sent, user_id_to_send, file_id, raw_file):
        sql = "INSERT INTO postcards (user_id_who_sent, user_id_to_sent, file_id, raw_file)" \
              " VALUES ($1, $2, $3, $4) returning *"
        return await self._execute(sql, user_id_who_sent, user_id_to_send, file_id, raw_file, fetchrow=True)

    async def count_postcards(self):
        sql = "SELECT COUNT(*) FROM postcards"
        return await self._execute(sql, fetchval=True)

    async def select_postcard(self, id):
        sql = "SELECT * FROM postcards WHERE id=$1"
        result = await self._execute(sql, id, fetchrow=True)
        return await self._format_postcard(result)

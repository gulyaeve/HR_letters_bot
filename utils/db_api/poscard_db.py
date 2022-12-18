import asyncio

from utils.db_api.db import Database


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
            time_created timestamp DEFAULT now()
        );
        """
        await self._execute(sql, execute=True)

    async def insert_postcard(self, user_id_who_sent, user_id_to_send, file_id, raw_file):
        sql = "INSERT INTO postcards (user_id_who_sent, user_id_to_sent, file_id, raw_file)" \
              " VALUES ($1, $2, $3, $4) returning *"
        return await self._execute(sql, user_id_who_sent, user_id_to_send, file_id, raw_file, fetchrow=True)

    async def count_postcards(self):
        sql = "SELECT COUNT(*) FROM postcards"
        return await self._execute(sql, fetchval=True)

    async def select_postcard(self, id):
        sql = "SELECT * FROM postcards WHERE id=$1"
        return await self._execute(sql, id, fetchrow=True)

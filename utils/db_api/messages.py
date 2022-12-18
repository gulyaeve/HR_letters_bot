import asyncio
from logging import log, INFO

from utils.db_api.db import Database


class Messages(Database):
    def __init__(self):
        super().__init__()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.create_tables())

    async def create_tables(self):
        sql = """
        CREATE TABLE IF NOT EXISTS messages_type_list (
            id SERIAL PRIMARY KEY,
            message_type text NOT NULL UNIQUE 
        );
        
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            description text NOT NULL UNIQUE,
            message_type integer REFERENCES messages_type_list(id),
            content text
        );
        """
        await self._execute(sql, execute=True)

    # Типы сообщений
    async def add_message_type(self, message_type):
        sql = "INSERT INTO messages_type_list (message_type) VALUES($1) returning *"
        return await self._execute(sql, message_type, fetchrow=True)

    async def select_message_type(self, **kwargs):
        sql = "SELECT * FROM messages_type_list WHERE "
        sql, parameters = self._format_args(sql, parameters=kwargs)
        return await self._execute(sql, *parameters, fetchrow=True)

    async def select_all_message_types(self):
        sql = "SELECT * FROM messages_type_list"
        return await self._execute(sql, fetch=True)

    # Сообщения
    async def add_message(self, description, message_type, content):
        sql = "INSERT INTO messages (description, message_type, content) VALUES($1, $2, $3) returning *"
        return await self._execute(sql, description, message_type, content, fetchrow=True)

    async def select_messages_by_type(self, message_type):
        sql = "SELECT * FROM messages WHERE message_type=$1"
        return await self._execute(sql, message_type, fetch=True)

    async def get_message_content(self, description):
        return await self._execute("SELECT content FROM messages WHERE description=$1", description, fetchval=True)

    async def get_message_content_by_id(self, message_id):
        return await self._execute("SELECT content FROM messages WHERE id=$1", message_id, fetchval=True)

    async def update_text_content(self, new_text, message_id):
        sql = "UPDATE messages SET content=$1 WHERE id=$2"
        return await self._execute(sql, new_text, message_id, execute=True)

    async def create_message_type(self, message_type: str):
        """
        Сохраняет тип сообщения в базе данных
        :param message_type: тип сообщения для сохранения в БД
        """
        exist_message_type = await self.select_message_type(message_type=message_type)
        if exist_message_type is None:
            new_message_type = await self.add_message_type(message_type)
            log(INFO, f"Message_type {message_type} success save in db")
            return new_message_type
        else:
            return exist_message_type

    async def create_message(self, description: str, message_type: int, content: str):
        """
        Сохраняет сообщение в базе данных
        :param description: описание сообщения
        :param message_type: ид типа сообщения из таблицы типов
        :param content: содержимое сообщения
        """
        message = await self.get_message(description)
        if message is None:
            await self.add_message(
                description=description,
                message_type=message_type,
                content=content
            )
            log(INFO, f"Message {description} success save in db")

    async def get_message(self, description: str) -> str:
        """
        Возвращает контент сообщения по описанию из базы данных
        :param description: description in database
        :return: content of message
        """
        try:
            return await self.get_message_content(description)
        except Exception as e:
            raise ValueError(e)


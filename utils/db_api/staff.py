import asyncio
from dataclasses import dataclass
from typing import Sequence

import asyncpg

from utils.db_api.db import Database


@dataclass
class Employee:
    id: int
    telegram_id: int | None
    lastname: str
    firstname: str
    middlename: str | None
    phone: str
    email: str
    day_birth: int | None
    month_birth: int | None

    def full_name(self):
        if self.middlename:
            return f"{self.lastname} {self.firstname} {self.middlename}"
        else:
            return f"{self.lastname} {self.firstname}"

    def __str__(self):
        result = f"{self.full_name()} "
        if self.email:
            result += "📧"
        if self.telegram_id:
            result += "💬"
        return result

    def info(self):
        auth = "🟢Авторизован в боте" if self.telegram_id is not None else "🔴Не авторизован в боте"
        info = f"{self.full_name()}\n" \
               f"Телефон: {self.phone}\n" \
               f"Email: {self.email}\n" \
               f"День рождения: {self.day_birth}\n" \
               f"Месяц рождения: {self.month_birth}\n" \
               f"{auth}"
        return info


class Employees:
    def __init__(self, users: Sequence[Employee]):
        self._users = users

    def __getitem__(self, key: int) -> Employee:
        return self._users[key]

    def __len__(self) -> int:
        return len(self._users)

    async def lastname_first_letters(self):
        letters = set()
        for user in self._users:
            letters.add(user.lastname[0])
        return sorted(list(letters))


class Staff(Database):
    def __init__(self):
        super().__init__()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.create_tables())

    async def create_tables(self):
        sql = """
        CREATE TABLE IF NOT EXISTS staff (
            id SERIAL PRIMARY KEY,
            telegram_id bigint UNIQUE DEFAULT NULL,
            lastname character varying(255),
            firstname character varying(255),
            middlename character varying(255),
            phone character varying(255),
            email character varying(255),
            day_birth integer NULL,
            month_birth integer NULL,
            time_created timestamp DEFAULT now()
        );
        """
        await self._execute(sql, execute=True)

    @staticmethod
    async def _format_employee(record: asyncpg.Record) -> Employee | None:
        if record:
            return Employee(
                id=record['id'],
                telegram_id=record['telegram_id'],
                lastname=record['lastname'],
                firstname=record['firstname'],
                middlename=record['middlename'],
                phone=record['phone'],
                email=record['email'],
                day_birth=record['day_birth'],
                month_birth=record['month_birth'],
            )
        else:
            return None

    async def add_employee(self, firstname, lastname, middlename, phone, email, day_birth, month_birth):
        sql = "INSERT INTO staff (firstname, lastname, middlename, phone, email, day_birth, month_birth) " \
              "VALUES($1, $2, $3, $4, $5, $6, $7) returning *"
        result = await self._execute(
            sql, firstname, lastname, middlename, phone, email, day_birth, month_birth,
            fetchrow=True)
        return await self._format_employee(result)

    async def select_all_employees(self) -> Employees:
        sql = "SELECT * FROM staff ORDER BY lastname ASC"
        list_of_records = await self._execute(sql, fetch=True)
        return Employees([await self._format_employee(record) for record in list_of_records])

    async def select_employee(self, **kwargs):
        sql = "SELECT * FROM staff WHERE "
        sql, parameters = self._format_args(sql, parameters=kwargs)
        record: asyncpg.Record = await self._execute(sql, *parameters, fetchrow=True)
        return await self._format_employee(record)

    async def update_employee_by_phone(self, telegram_id, phone):
        sql = "UPDATE staff SET telegram_id=$1 WHERE phone=$2"
        return await self._execute(sql, telegram_id, phone, execute=True)

    async def update_employee_by_email(self, telegram_id, email):
        sql = "UPDATE staff SET telegram_id=$1 WHERE email=$2"
        return await self._execute(sql, telegram_id, email, execute=True)

    async def logout_employee(self, telegram_id):
        sql = "UPDATE staff SET telegram_id=NULL WHERE telegram_id=$1"
        return await self._execute(sql, telegram_id, execute=True)

    async def find_employee(self, keyword):
        sql = "SELECT * FROM staff WHERE LOWER(concat(lastname, ' ', firstname)) LIKE '%' || LOWER($1) || '%'"
        list_of_records = await self._execute(sql, keyword, fetch=True)
        return Employees([await self._format_employee(record) for record in list_of_records])

    async def delete_employee(self, id):
        await self._execute("DELETE FROM staff WHERE id=$1", id, execute=True)

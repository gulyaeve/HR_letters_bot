import asyncio

from utils.db_api.db import Database


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
        await self.execute(sql, execute=True)

    async def add_employee(self, firstname, lastname, middlename, phone, email, day_birth, month_birth):
        sql = "INSERT INTO staff (firstname, lastname, middlename, phone, email, day_birth, month_birth) " \
              "VALUES($1, $2, $3, $4, $5, $6, $7) returning *"
        return await self.execute(sql, firstname, lastname, middlename, phone, email, day_birth, month_birth,
                                  fetchrow=True)

    async def select_employee(self, **kwargs):
        sql = "SELECT * FROM staff WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def update_employee_by_phone(self, telegram_id, phone):
        sql = "UPDATE staff SET telegram_id=$1 WHERE phone=$2"
        return await self.execute(sql, telegram_id, phone, execute=True)

    async def update_employee_by_email(self, telegram_id, email):
        sql = "UPDATE staff SET telegram_id=$1 WHERE email=$2"
        return await self.execute(sql, telegram_id, email, execute=True)

    async def logout_employee(self, user_id):
        sql = "UPDATE staff SET telegram_id=NULL WHERE id=$1"
        return await self.execute(sql, user_id, execute=True)

    async def find_employee(self, keyword):
        sql = "SELECT * FROM staff WHERE LOWER(concat(lastname, ' ', firstname)) LIKE '%' || LOWER($1) || '%'"
        return await self.execute(sql, keyword, fetch=True)

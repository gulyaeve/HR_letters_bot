from logging import log, INFO

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from config import Config
from loader import users


class ManagerCheck(BoundFilter):
    async def check(self, message: types.Message):
        """
        Фильтр для проверки менеджера
        """
        # manager_user_type = await users.select_user_type("manager")
        user = await users.select_user(telegram_id=message.from_user.id)
        try:
            if str(message.from_user.id) in Config.bot_admins or user.type == 'manager' or user.type == 'admin':
                log(INFO, f"[{message.from_user.id=}] пользователь является менеджером")
                return True
            else:
                log(INFO, f"Пользователь не является менеджером [{message.from_user.id=}]")
                return False
        except Exception as err:
            log(INFO, f"[{message.from_user.id=}] менеджер не найден. {err}")
            return False

from logging import log, INFO

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from config import Config
from loader import users


class AdminCheck(BoundFilter):
    async def check(self, message: types.Message):
        """
        Фильтр для проверки админа
        """
        user = await users.select_user(telegram_id=message.from_user.id)
        try:
            if str(message.from_user.id) in Config.bot_admins or user.type == "admin":
                log(INFO, f"[{message.from_user.id=}] пользователь является админом")
                return True
            else:
                log(INFO, f"Пользователь не является админом [{message.from_user.id=}]")
                return False
        except Exception as err:
            log(INFO, f"[{message.from_user.id=}] админ не найден. {err}")
            return False

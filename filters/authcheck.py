from logging import log, INFO

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from loader import staff


class AuthCheck(BoundFilter):
    async def check(self, message: types.Message):
        """
        Фильтр для проверки авторизации
        """
        try:
            user = await staff.select_employee(telegram_id=message.from_user.id)
            if user['telegram_id'] is None:
                log(INFO, f"Пользователь не прошёл регистрацию [{message.from_user.id=}]")
                return False
            else:
                log(INFO, f"[{message.from_user.id=}] пользователь прошёл регистрацию: [{user['telegram_id']=}]")
                return True
        except Exception as err:
            log(INFO, f"[{message.from_user.id=}] Пользователь не найден. {err}")
            return False

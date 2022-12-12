from logging import log, INFO

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from handlers.admins.admins import notify_admins
from loader import users


class DBmiddleware(BaseMiddleware):
    async def on_pre_process_update(self, update: types.Update, data: dict):
        log(INFO, update)
        pass

    async def on_pre_process_message(self, message: types.Message, data: dict):
        try:
            user = await users.select_user(message.from_user.id)
            if user is not None:
                if user.full_name != message.from_user.full_name:
                    await users.update_user_fullname(message.from_user.full_name, message.from_user.id)
                    log(INFO, f"Updated full_name [{message.from_user.full_name}] for [{message.from_user.id}]")
                if user.username != message.from_user.username:
                    await users.update_user_username(message.from_user.username, message.from_user.id)
                    log(INFO, f"Updated username [{message.from_user.username}] for [{message.from_user.id}]")
        except:
            new_user = await users.add_user(message.from_user.full_name, message.from_user.username, message.from_user.id)
            await notify_admins(f"<b>Добавлен пользователь:</b>\n{new_user.get_info()}")
            log(INFO, f"Added user to db [{new_user}]")

    # async def on_process_message(self, message: types.Message, data: dict):
    #     user = await users.select_user(telegram_id=message.from_user.id)
    #     log(INFO, f"{user=}")
    #     if user is not None:
    #         data["id"] = str(user.id)

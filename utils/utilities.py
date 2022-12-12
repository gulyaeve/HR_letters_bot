import io
import os
import re

from aiogram import types

from loader import dp, users
from utils.db_api.usersdb import Users


async def get_bot_info() -> types.User:
    me = await dp.bot.get_me()
    return me


async def get_users_file() -> types.InputFile:
    filename = "users.txt"
    list_users: Users = await users.select_all_users()
    answer = "{:11} {:25} {:20} {:11} {:10}\n".format(
        "telegram_id", "full_name", "username", "phone", "user_type"
    )
    for user in list_users:
        answer += "{:11} {:25} {:20} {:11} {:10}\n".format(
            user.telegram_id,
            user.full_name,
            user.username,
            user.phone,
            user.type
        )
    return types.InputFile(io.BytesIO(make_bytes(answer, filename)), filename)


def make_keyboard_dict(buttons: dict):
    keyboard = types.ReplyKeyboardMarkup()
    for button in buttons.values():
        keyboard.add(button)
    keyboard.add("ОТМЕНА")
    return keyboard


def make_keyboard_list(buttons: list):
    keyboard = types.ReplyKeyboardMarkup()
    for button in buttons:
        keyboard.add(button)
    keyboard.add("ОТМЕНА")
    return keyboard


def make_text(input_text):
    return re.sub(r'<.*?>', '', input_text)


def make_bytes(file_content: str, file_label: str) -> bytes:
    with open(f"temp/{file_label}", "w") as f:
        f.write(file_content)
    with open(f"temp/{file_label}", "rb") as f:
        file = f.read()
        b = bytearray(file)
    os.remove(f"temp/{file_label}")
    return b


def make_dict_output(d: types.User) -> str:
    result = ''
    d = dict(d)
    for key, value in d.items():
        result += "{0}: {1}\n".format(key, value)
    return result

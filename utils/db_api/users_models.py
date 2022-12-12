import json
from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from aiogram.types import InlineKeyboardButton

with open("templates/type_users_template.json", "r", encoding="utf-8") as file:
    new_types = json.loads(file.read())
    UserTypes = Enum('UserTypes', new_types['type_users'])


@dataclass
class User:
    telegram_id: int
    full_name: str
    username: str
    phone: str
    type: UserTypes

    def make_button(self):
        type_emoji = self.type
        match self.type:
            case "user":
                type_emoji = "👤"
            case "manager":
                type_emoji = "💼"
            case "admin":
                type_emoji = "👑"
        link = f"@{self.username}" if self.username is not None else self.telegram_id
        return InlineKeyboardButton(
            text=f"{self.full_name} {link} {type_emoji}",
            callback_data=f"user={self.telegram_id}",
        )

    def get_info(self) -> str:
        return f"telegram_id: <code>{self.telegram_id}</code>\n" \
               f"full_name: <code>{self.full_name}</code>\n"\
               f"link: {self.mention}\n" \
               f"phone: <code>{self.phone}</code>\n"\
               f"type: <code>{self.type}</code>\n"

    @property
    def mention(self):
        if self.username:
            return '@' + self.username
        return self.url

    @property
    def url(self) -> str:
        return f"tg://user?id={self.telegram_id}"


class Users:
    def __init__(self, users: Sequence[User]):
        self._users = users

    def __getitem__(self, key: int) -> User:
        return self._users[key]

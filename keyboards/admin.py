import enum

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class AdminCallbacks(enum.Enum):
    get_users = "get_users"
    create_mailing = "create_mailing"
    text_messages = "text_messages"
    # manage_users = "manage_users"


class AdminsMenu:
    admin_main_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Пользователи",
                                     callback_data=AdminCallbacks.get_users.value)
            ],
            [
                InlineKeyboardButton(text="Создать рассылку",
                                     callback_data=AdminCallbacks.create_mailing.value)
            ],
            [
                InlineKeyboardButton(text="Тексты сообщений",
                                     callback_data=AdminCallbacks.text_messages.value)
            ],
        ]
    )

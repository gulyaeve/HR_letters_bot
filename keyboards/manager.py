import enum

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class ManagerCallbacks(enum.Enum):
    # get_users = "get_users"
    create_mailing = "create_mailing_manager"
    staff = "staff"
    postcards = "postcards"
    # text_messages = "text_messages"
    # manage_users = "manage_users"


class ManagersMenu:
    manager_main_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Создать рассылку",
                    callback_data=ManagerCallbacks.create_mailing.value,
                )
            ],
            [
                InlineKeyboardButton(
                    text="Сотрудники",
                    callback_data=ManagerCallbacks.staff.value,
                )
            ],
            [
                InlineKeyboardButton(
                    text="Открытки",
                    callback_data=ManagerCallbacks.postcards.value,
                )
            ],
        ]
    )

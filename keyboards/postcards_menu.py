import enum

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class PostcardMenu(enum.Enum):
    left = "left"
    right = "right"
    ok = "ok"
    back = "back"
    decline = "decline"
    accept = "accept"


class PostcardSelector:
    postcards_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️",
                    callback_data=PostcardMenu.left.value
                ),
                InlineKeyboardButton(
                    text="⏪️",
                    callback_data=PostcardMenu.back.value
                ),
                InlineKeyboardButton(
                    text="🆗️",
                    callback_data=PostcardMenu.ok.value
                ),
                InlineKeyboardButton(
                    text="➡️️",
                    callback_data=PostcardMenu.right.value
                ),
            ],

        ]
    )
    postcards_accept_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏪️",
                    callback_data=PostcardMenu.decline.value
                ),
                InlineKeyboardButton(
                    text="✅",
                    callback_data=PostcardMenu.accept.value
                ),
            ],
        ]
    )


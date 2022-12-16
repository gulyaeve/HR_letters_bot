from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.my_paginator import MyPaginator

page_size = 4


async def make_inline_categories(categories: [str], current_page: int):
    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    for category in categories:
        inline_keyboard.add(
            InlineKeyboardButton(
                text=category,
                callback_data=f"category={category}",
            )
        )
    if len(categories) > page_size:
        paginator = MyPaginator(data=inline_keyboard, size=page_size)
        keyboard = paginator(current_page)
    else:
        keyboard = inline_keyboard
    return keyboard

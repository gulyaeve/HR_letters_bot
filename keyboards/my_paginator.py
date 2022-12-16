
from aiogram import types
from aiogram_inline_paginations.paginator import Paginator


class MyPaginator(Paginator):
    @staticmethod
    def _get_paginator(
            counts: int,
            page: int,
            page_separator: str = '/',
            startswith: str = 'page_'
    ) -> list[types.InlineKeyboardButton]:
        counts -= 1

        paginations = []

        if page > 0:
            paginations.append(
                types.InlineKeyboardButton(
                    text='Назад',
                    callback_data=f'{startswith}{page - 1}'
                ),
            )
        if counts > page:
            paginations.append(
                types.InlineKeyboardButton(
                    text='Далее',
                    callback_data=f'{startswith}{page + 1}'
                )
            )
        return paginations

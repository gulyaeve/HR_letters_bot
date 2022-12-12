import logging

from aiogram import types
from aiogram.dispatcher.filters import Text

from keyboards.admin import AdminCallbacks
from loader import dp, users
from aiogram_inline_paginations.paginator import Paginator


@dp.callback_query_handler(Text(startswith='userspage_'))
@dp.callback_query_handler(text=AdminCallbacks.get_users.value)
async def get_users(callback: types.CallbackQuery):
    await callback.answer("Выгружаю")
    page_n = 0
    if callback.data.startswith("userspage_"):
        page_n = int(callback.data.split("_")[1])
    users_list = await users.select_all_users()
    buttons_users = types.InlineKeyboardMarkup()
    for user in users_list:
        buttons_users.add(user.make_button())
    logging.info(buttons_users)
    users_inline = Paginator(callback_startswith="userspage_", data=buttons_users)
    await callback.message.edit_text("Готово:", reply_markup=users_inline(current_page=page_n))

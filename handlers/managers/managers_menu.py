import logging

from aiogram import types

from filters import ManagerCheck
from keyboards.manager import ManagersMenu
from loader import dp, messages


@dp.message_handler(ManagerCheck(), commands=['manage', 'manager'])
async def admin_start(message: types.Message):
    logging.info(f"{message.from_user.id=} passed to admin menu")
    await message.answer(
        await messages.get_message("manager_menu"),
        reply_markup=ManagersMenu.manager_main_menu
    )

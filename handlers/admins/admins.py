from logging import log, INFO

from aiogram import types
from aiogram.dispatcher import FSMContext

from config import Config
from filters import AdminCheck
from keyboards.admin import AdminsMenu
from loader import dp, messages, users


async def notify_admins(message: str):
    admin_user_type = await users.select_user_type("admin")
    admins = await users.select_users_by_type(admin_user_type)
    for admin in admins:
        try:
            await dp.bot.send_message(admin.telegram_id, message)
        except Exception as e:
            log(INFO, f"Failed to notify Admin [{admin.telegram_id}] ({e})")
    for bot_admin in Config.bot_admins:
        try:
            await dp.bot.send_message(bot_admin, message)
        except Exception as e:
            log(INFO, f"Failed to notify Admin [{bot_admin}] ({e})")


@dp.message_handler(AdminCheck(), commands=['admin'])
async def admin_start(message: types.Message):
    log(INFO, f"{message.from_user.id=} passed to admin menu")
    await message.answer(await messages.get_message("admin_menu"), reply_markup=AdminsMenu.admin_main_menu)


@dp.callback_query_handler(text="back_to_main_admin_menu", state="*")
async def admin_start(callback: types.CallbackQuery, state: FSMContext):
    log(INFO, f"{callback.message.from_user.id=} passed to admin menu")
    await callback.message.edit_text(await messages.get_message("admin_menu"), reply_markup=AdminsMenu.admin_main_menu)
    await state.finish()

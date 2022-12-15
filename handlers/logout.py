from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove

from keyboards import keyboards
from loader import dp, staff, messages
from logging import log, INFO
from filters import AuthCheck


@dp.message_handler(AuthCheck(), commands=["logout"])
async def cmd_logout_auth(message: types.Message, state: FSMContext):
    await message.reply(await messages.get_message("logout_confirm"), reply_markup=keyboards.yes_no)
    await state.set_state("confirm")


@dp.message_handler(commands=["logout"])
async def cmd_logout_all(message: types.Message):
    await message.reply(await messages.get_message("auth_mention"))


@dp.message_handler(Text(equals="да", ignore_case=True), state="confirm")
async def logout_yes(message: types.Message, state: FSMContext):
    log(INFO, f"Logout [{message.from_user.id=}], [{message.from_user.username=}]")
    await staff.logout_employee(message.from_user.id)
    await message.reply(await messages.get_message("logout_success"),
                        reply_markup=ReplyKeyboardRemove())
    await state.finish()


@dp.message_handler(Text(equals="нет", ignore_case=True), state="confirm")
async def logout_no(message: types.Message, state: FSMContext):
    await message.reply(await messages.get_message("logout_cancel"), reply_markup=ReplyKeyboardRemove())
    await state.finish()

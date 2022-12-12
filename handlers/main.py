
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from logging import log, INFO

from loader import dp, messages
from utils.utilities import get_bot_info


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    help_message = await messages.get_message("help_message")
    await message.answer(help_message)


@dp.message_handler(commands=['start'])
async def cmd_start_user(message: types.Message):
    """
    Conversation's entry point
    """
    log(INFO, f"[{message.from_user.id=}] нажал START.")
    me = await get_bot_info()
    welcome_message = await messages.get_message("welcome")
    await message.reply(welcome_message.format(me.full_name))
    await message.answer(await messages.get_message("welcome_help_hint"))


# You can use state '*' if you need to handle all states
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
@dp.message_handler(state='*', commands=['cancel'])
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    log(INFO, f"[{message.from_user.id=}] отменил действие.")
    await state.finish()
    await message.reply(await messages.get_message("cancel"), reply_markup=types.ReplyKeyboardRemove())

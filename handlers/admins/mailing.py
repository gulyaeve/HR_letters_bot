import asyncio
from logging import log, INFO

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from keyboards.admin import AdminCallbacks
from loader import dp, users, messages
from utils.db_api.usersdb import Users


class Mailing(StatesGroup):
    SendMessage = State()


@dp.callback_query_handler(text=AdminCallbacks.create_mailing.value)
async def create_mailing(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(await messages.get_message("mailing_start"),
                                     reply_markup=None)
    await Mailing.SendMessage.set()


@dp.message_handler(state=Mailing.SendMessage, content_types=types.ContentType.ANY)
async def send_mailing(message: types.Message, state: FSMContext):
    users_to_send: Users = await users.select_all_users()
    for user in users_to_send:
        await asyncio.sleep(0.1)
        try:
            await dp.bot.copy_message(user.telegram_id, message.from_id, message.message_id)
            log(INFO, f"Рассылка успешно отправлена пользователю {user.telegram_id}")
        except Exception as e:
            log(INFO, f"Ошибка при отправке рассылки пользователю {user.telegram_id}: {e}")
    await message.answer(await messages.get_message("mailing_finish"))
    await state.finish()

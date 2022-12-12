from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from logging import log, INFO, WARN

from loader import dp, users


async def copy_to_managers(message: types.Message):
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Ответить", callback_data=f'reply_from_anytext_id={message.from_user.id}')]])
    manager_user_type = await users.select_user_type("manager")
    managers = await users.select_users_by_type(manager_user_type)
    for manager in managers:
        try:
            await dp.bot.copy_message(manager.telegram_id,
                                      message.chat.id,
                                      message.message_id,
                                      "Сообщение от пользователя",
                                      reply_markup=inline_keyboard)
        except Exception as e:
            log(WARN, f"Failed to send to [{manager}] {e}")


@dp.callback_query_handler(Regexp('reply_from_anytext_id=([0-9]*)'))
async def answer_to_text(callback: types.CallbackQuery, state: FSMContext):
    reply_user_id = callback.data.split("=")[1]
    async with state.proxy() as data:
        data["reply_user_id"] = reply_user_id
    await callback.message.answer(f"Введите ответ:")
    await state.set_state("ANSWER_TO_ANY_TEXT")


@dp.message_handler(state="ANSWER_TO_ANY_TEXT", content_types=types.ContentType.ANY)
async def send_answer_to_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        await dp.bot.copy_message(data['reply_user_id'], message.from_id, message.message_id)
        log(INFO, f'Пользователю [{data["reply_user_id"]=}] отправлено: {message.message_id}')
        await message.answer('Сообщение отправлено')
    except Exception as e:
        await message.answer('Ошибка при отправке')
        log(INFO, f"Failed to send message: {e}")
    await state.finish()

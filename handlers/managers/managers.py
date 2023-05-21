from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from logging import log, INFO, WARN

from config import Config
from loader import dp, users


async def file_to_managers(file):
    manager_user_type = await users.select_user_type("manager")
    managers = await users.select_users_by_type(manager_user_type)
    for manager in managers:
        try:
            await dp.bot.send_document(manager.telegram_id, file)
        except Exception as e:
            log(INFO, f"Failed to notify Manager [{manager.telegram_id}] ({e})")


async def notify_managers(message: str):
    manager_user_type = await users.select_user_type("manager")
    managers = await users.select_users_by_type(manager_user_type)
    for manager in managers:
        try:
            await dp.bot.send_message(manager.telegram_id, message)
        except Exception as e:
            log(INFO, f"Failed to notify Manager [{manager.telegram_id}] ({e})")
    for bot_admin in Config.bot_admins:
        try:
            await dp.bot.send_message(bot_admin, message)
        except Exception as e:
            log(INFO, f"Failed to notify Admin [{bot_admin}] ({e})")


async def copy_to_managers(message: types.Message):
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Ответить", callback_data=f'reply_from_anytext_id={message.from_user.id}')]])
    manager_user_type = await users.select_user_type("manager")
    admin_user_type = await users.select_user_type("admin")
    managers = await users.select_users_by_type(manager_user_type)
    admins = await users.select_users_by_type(admin_user_type)
    for manager in managers:
        try:
            await dp.bot.copy_message(manager.telegram_id,
                                      message.chat.id,
                                      message.message_id,
                                      "Сообщение от пользователя",
                                      reply_markup=inline_keyboard)
        except Exception as e:
            log(WARN, f"Failed to send to [{manager}] {e}")
    for admin in admins:
        try:
            await dp.bot.copy_message(admin.telegram_id,
                                      message.chat.id,
                                      message.message_id,
                                      "Сообщение от пользователя",
                                      reply_markup=inline_keyboard)
        except Exception as e:
            log(WARN, f"Failed to send to [{admin}] {e}")


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

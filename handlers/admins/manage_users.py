from logging import log, INFO

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp, Text

from loader import dp, users
from utils.utilities import make_dict_output


@dp.callback_query_handler(Text(startswith="user="))
async def choose_action(callback: types.CallbackQuery):
    await callback.message.delete()
    user_id = int(callback.data.split("=")[1])
    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(
        types.InlineKeyboardButton(
            text="Изменить права пользователя ❇️",
            callback_data=f"set_user={user_id}",
        )
    )
    inline_keyboard.add(
        types.InlineKeyboardButton(
            text="Информация ℹ️",
            callback_data=f"user_info={user_id}"
        )
    )
    inline_keyboard.add(types.InlineKeyboardButton(text="◀️", callback_data="back_to_main_admin_menu"))
    await callback.message.answer("Выберите действие:", reply_markup=inline_keyboard)


@dp.callback_query_handler(Text(startswith="set_user="))
async def choose_user(callback: types.CallbackQuery):
    user_id = int(callback.data.split("=")[1])
    user_to_set = await users.select_user(user_id)
    user_info = f"{user_to_set.full_name}, @{user_to_set.username}"
    user_types = await users.select_all_user_types()
    inline_keyboard = types.InlineKeyboardMarkup()
    for user_type in user_types:
        inline_keyboard.add(
            types.InlineKeyboardButton(
                text=user_type['name'],
                callback_data=f"set_user_type={user_id}={user_type['id']}"
            )
        )
    await callback.message.edit_text(f"Выберите кем назначить <b>{user_info}?</b>:", reply_markup=inline_keyboard)


@dp.callback_query_handler(Regexp('set_user_type=([0-9]*)=([0-9]*)'))
async def set_user_type(callback: types.CallbackQuery):
    user_to_set = await users.select_user(int(callback.data.split('=')[1]))
    type_id = int(callback.data.split('=')[2])
    type_name = await users.select_user_type_dy_id(type_id)
    await users.update_user_type(type_id, user_to_set.telegram_id)
    log(INFO, f"{callback.from_user.id} set new {type_id=} to {user_to_set}")
    try:
        await dp.bot.send_message(user_to_set.telegram_id, f"Вам назначена роль: <b>{type_name}</b>")
    except Exception as e:
        log(INFO, f"Failed to send to [{user_to_set.telegram_id}] {e}")
    await callback.message.edit_text(f"Вы назначили роль: <b>{type_name}</b> для\n{user_to_set}")
    await callback.answer(f"Вы назначили роль {type_name}\n\nПользователю {user_to_set.full_name}", show_alert=True)


@dp.callback_query_handler(Text(startswith="user_info="))
async def get_user_info(callback: types.CallbackQuery):
    await callback.message.delete()
    user_id = int(callback.data.split("=")[1])
    info_from_dp = await users.select_user(user_id)
    info_from_telegram = await dp.bot.get_chat(user_id)
    photo = info_from_telegram.photo.big_file_id
    useful_info_from_telegram = info_from_telegram.to_python()
    del useful_info_from_telegram['photo']
    file = await dp.bot.download_file_by_id(photo)
    answer = f"<b>Информация из моей базы:</b>\n{info_from_dp.get_info()}\n" \
             f"<b>Информация из телеграм:</b>\n{make_dict_output(useful_info_from_telegram)}"
    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(
        types.InlineKeyboardButton(
            text="Отправить личное сообщение 💬",
            callback_data=f"private_msg={user_id}"
        )
    )
    inline_keyboard.add(
        types.InlineKeyboardButton(
            text="⏮",
            callback_data=f"user={user_id}",
        )
    )
    await callback.message.answer_photo(photo=file.getbuffer().tobytes(),
                                        caption=answer,
                                        reply_markup=inline_keyboard)


@dp.callback_query_handler(Regexp('private_msg=([0-9]*)'))
async def answer_to_text(callback: types.CallbackQuery, state: FSMContext):
    reply_user_id = callback.data.split("=")[1]
    async with state.proxy() as data:
        data["private_user_id"] = reply_user_id
    await callback.message.answer(f"Введите сообщение:")
    await state.set_state("PRIVATE_MSG")


@dp.message_handler(state="PRIVATE_MSG", content_types=types.ContentType.ANY)
async def send_answer_to_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        await dp.bot.copy_message(data['private_user_id'], message.from_id, message.message_id)
        log(INFO, f'Пользователю [{data["private_user_id"]=}] отправлено: {message.message_id}')
        await message.answer('Сообщение отправлено')
    except Exception as e:
        await message.answer('Ошибка при отправке')
        log(INFO, f"Failed to send message: {e}")
    await state.finish()

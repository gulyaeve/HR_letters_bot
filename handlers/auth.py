from logging import log, INFO

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from handlers.admins.admins import notify_admins
from keyboards.keyboards import auth_phone
from loader import dp, users, messages


class Auth(StatesGroup):
    Phone = State()


@dp.message_handler(commands=['auth'])
async def auth_user(message: types.Message):
    await message.reply(await messages.get_message('auth_start'), reply_markup=auth_phone)
    await Auth.Phone.set()


@dp.message_handler(state=Auth.Phone, content_types=types.ContentType.CONTACT)
async def phone_confirm(message: types.Message, state: FSMContext):
    if message.contact.user_id == message.from_user.id:
        log(INFO, f"Update phone {message.contact.phone_number} for {message.from_user.id}")
        await users.update_user_phone(message.contact.phone_number, message.from_user.id)
        await message.reply(await messages.get_message('success_auth'), reply_markup=types.ReplyKeyboardRemove())
        user = await users.select_user(message.from_user.id)
        await notify_admins(f"<b>Пользователь авторизовался:</b>\n{user.get_info()}")
        await state.finish()
    else:
        user = await users.select_user(message.from_user.id)
        await notify_admins(f"<b>ПОЛЬЗОВАТЕЛЬ ПЫТАЛСЯ АВТОРИЗОВАТЬСЯ ПО ЧУЖОМУ НОМЕРУ:</b>\n"
                            f"{user.get_info()}\n\n"
                            f"wrong_contact: <code>{message.contact.full_name}</code>\n"
                            f"wrong_user_id: <code>{message.contact.user_id}</code>\n"
                            f"wrong_phone: <code>{message.contact.phone_number}</code>\n"
                            f"wrong_link: tg://user?id={message.contact.user_id}\n")
        return await message.reply(await messages.get_message('wrong_phone'))


@dp.message_handler(state=Auth.Phone, content_types=types.ContentType.ANY)
async def no_phone(message: types.Message, state: FSMContext):
    await message.reply(await messages.get_message('wrong_number'), reply_markup=types.ReplyKeyboardRemove())
    await state.finish()

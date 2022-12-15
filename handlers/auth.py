from logging import log, INFO
from random import randrange
from re import match

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove

from filters import AuthCheck
from handlers.admins.admins import notify_admins
from keyboards.keyboards import auth_phone, choose_auth
from loader import dp, users, messages, staff
from utils.email_sender import send_email
from utils.utilities import get_bot_info

email_pattern = r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"


class Auth(StatesGroup):
    ChooseMethod = State()
    Phone = State()
    Email = State()
    Code = State()


@dp.message_handler(AuthCheck(), commands=['auth'])
async def cmd_auth_already(message: types.Message):
    await message.reply(await messages.get_message("auth_already"))


@dp.message_handler(commands=['auth'])
async def auth_method(message: types.Message):
    await message.reply(await messages.get_message('auth_method'), reply_markup=choose_auth)
    await Auth.ChooseMethod.set()


@dp.message_handler(Text(startswith='Номер'), state=Auth.ChooseMethod)
async def auth_user_phone(message: types.Message):
    await message.reply(await messages.get_message('auth_start'), reply_markup=auth_phone)
    await Auth.Phone.set()


@dp.message_handler(Text(startswith='Email'), state=Auth.ChooseMethod)
async def auth_user_email(message: types.Message):
    log(msg=f"Start authentication by EMAIL for [{message.from_user.id=}], [{message.from_user.username=}]",
        level=INFO)
    await message.reply(await messages.get_message("auth_email_start"), reply_markup=ReplyKeyboardRemove())
    await Auth.Email.set()


@dp.message_handler(state=Auth.Phone, content_types=types.ContentType.CONTACT)
async def phone_confirm(message: types.Message, state: FSMContext):
    if message.contact.user_id == message.from_user.id:
        phone = message.contact.phone_number.replace('+', '')
        employee = await staff.select_employee(phone=phone)
        if employee is not None:
            log(INFO, f"Update phone {message.contact.phone_number} for {message.from_user.id}")
            await users.update_user_phone(message.contact.phone_number, message.from_user.id)
            await staff.update_employee_by_phone(message.from_user.id, phone)
            await message.reply(await messages.get_message('success_auth'), reply_markup=types.ReplyKeyboardRemove())
            user = await users.select_user(message.from_user.id)
            await notify_admins(f"<b>Пользователь авторизовался:</b>\n{user.get_info()}")
            await state.finish()
        else:
            log(msg=f"Invalid [{message.contact.phone_number=}]; [{message.from_user.id=}]", level=INFO)
            await message.answer(await messages.get_message("failed_phone_employee"),
                                 reply_markup=ReplyKeyboardRemove())
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


@dp.message_handler(state=Auth.Email)
async def enter_code(message: types.Message, state: FSMContext):
    email = message.text.lower()
    if match(email_pattern, message.text):
        user = await staff.select_employee(email=email)
        if user is not None:
            code = randrange(1, 10 ** 6)
            log(msg=f"Generate [{code=}]; [{user['id']=}]; [{email=}]; [{message.from_user.id=}]",
                level=INFO)
            me = await get_bot_info()
            await send_email(email, f"{me.full_name} Authorization", f"Здраствуйте! Ваш код подтверждения: {code}")
            await message.answer(await messages.get_message("auth_email_code"))
            async with state.proxy() as data:
                data["email"] = email
                data["code"] = code
            await Auth.Code.set()
        else:
            log(msg=f"Failed [{email=}]; [{message.from_user.id=}]", level=INFO)
            await message.answer(await messages.get_message("auth_email_fail"))
            await state.finish()
    else:
        log(msg=f"Invalid [{email=}]; [{message.from_user.id=}]", level=INFO)
        return await message.answer(await messages.get_message("auth_email_invalid"))


@dp.message_handler(state=Auth.Code)
async def code_confirm(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == str(data["code"]):
        log(msg=f"Enter valid code[{message.text}]; [{message.from_user.id=}]", level=INFO)
        await staff.update_employee_by_email(message.from_user.id, data['email'])
        user = await users.select_user(telegram_id=message.from_user.id)
        log(INFO, f"Success update in DB: [{user=}]")
        await notify_admins(f"<b>Пользователь авторизовался по Email:</b>\n{user.get_info()}")
        await message.answer(await messages.get_message("success_auth"))
        # await message.answer("Теперь давай отправим твоему коллеге «Спасибо»! Нажми <b>/say_thanks</b>")
        await state.finish()
    else:
        log(msg=f"Enter wrong code[{message.text}]; [{message.from_user.id=}]", level=INFO)
        return await message.answer(await messages.get_message("wrong_code"))

import logging
from re import match

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp

from filters import AuthCheck
from handlers.managers.managers import copy_to_managers
from handlers.send_postcard import Thanks
from loader import dp, staff, messages


@dp.message_handler(AuthCheck(), Regexp(r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"))
async def search_by_email(message: types.Message, state: FSMContext):
    logging.info(f"Start search by email [{message.from_user.id=}] request[{message.text=}]")
    search_email = message.text.lower()
    result = await staff.select_employee(email=search_email)
    if result:
        await message.answer(
            (await messages.get_message("email_search_success")).format(result.full_name())
        )
        async with state.proxy() as data:
            data['employee_id_to_sent'] = result.id
        await message.answer(
            await messages.get_message("input_text"),
        )
        await Thanks.TypeMessage.set()
    else:
        return await message.answer(
            await messages.get_message("email_search_failed")
        )


@dp.message_handler(AuthCheck(), content_types=types.ContentType.TEXT)
async def search_by_name(message: types.Message):
    logging.info(f"Start search by name [{message.from_user.id=}] request[{message.text=}]")
    search = message.text.replace('ё', 'е')
    results = await staff.find_employee(search)
    inline_keyboard = types.InlineKeyboardMarkup()
    for employee in results:
        if employee:
            inline_keyboard.add(
                types.InlineKeyboardButton(
                    text=f"{str(employee)}",
                    callback_data=f"employee={employee.id}"
                )
            )
    logging.info(f"{results=} {inline_keyboard.to_python()['inline_keyboard']=}")
    if len(inline_keyboard.to_python()['inline_keyboard']) > 0:
        await message.answer("Найдено:", reply_markup=inline_keyboard)
    else:
        await copy_to_managers(message)

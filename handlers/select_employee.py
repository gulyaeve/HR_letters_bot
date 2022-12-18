from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram_inline_paginations.paginator import Paginator

from filters import AuthCheck
from loader import dp, staff, messages


@dp.message_handler(AuthCheck(), commands=['send_postcard'])
async def select_employee(message: types.Message):
    all_employees = await staff.select_all_employees()
    letters_list = await all_employees.lastname_first_letters()
    inline_keyboard = types.InlineKeyboardMarkup(row_width=7)
    for letter in letters_list:
        inline_keyboard.insert(
            types.InlineKeyboardButton(
                text=letter,
                callback_data=f'employee_letter={letter}'
            )
        )
    await message.answer(
        await messages.get_message('choose_letter'),
        reply_markup=inline_keyboard
    )


@dp.callback_query_handler(Text(equals="back_to_letters"))
async def back_select_employee(callback: types.CallbackQuery):
    all_employees = await staff.select_all_employees()
    letters_list = await all_employees.lastname_first_letters()
    inline_keyboard = types.InlineKeyboardMarkup(row_width=7)
    for letter in letters_list:
        inline_keyboard.insert(
            types.InlineKeyboardButton(
                text=letter,
                callback_data=f'employee_letter={letter}'
            )
        )
    await callback.message.edit_text(
        await messages.get_message('choose_letter'),
        reply_markup=inline_keyboard
    )


@dp.callback_query_handler(Text(startswith='employee_letter='))
async def choose_employee_by_letter(callback: types.CallbackQuery):
    letter = callback.data.split('=')[1]
    all_employees = await staff.select_all_employees()
    inline_keyboard = types.InlineKeyboardMarkup()
    for employee in all_employees:
        if employee.lastname[0] == letter:
            inline_keyboard.add(
                types.InlineKeyboardButton(
                    text=f"{employee.full_name()}",
                    callback_data=f"employee={employee.id}"
                )
            )
    paginator = Paginator(inline_keyboard, callback_startswith=f'employees_{letter}_')
    keyboard = paginator()
    keyboard.add(
        types.InlineKeyboardButton(
            text="◀️",
            callback_data='back_to_letters'
        )
    )
    await callback.message.delete()
    await callback.message.answer(
        await messages.get_message('choose_employee_name'),
        reply_markup=keyboard
    )


@dp.callback_query_handler(Text(startswith="employees_"))
async def choose_employee_by_letter_page(callback: types.CallbackQuery):
    letter = callback.data.split("_")[1]
    page = int(callback.data.split("_")[2])

    all_employees = await staff.select_all_employees()
    inline_keyboard = types.InlineKeyboardMarkup()
    for employee in all_employees:
        if employee.lastname[0] == letter:
            inline_keyboard.add(
                types.InlineKeyboardButton(
                    text=f"{employee.full_name()}",
                    callback_data=f"employee={employee.id}"
                )
            )
    paginator = Paginator(inline_keyboard, callback_startswith=f'employees_{letter}_')
    keyboard = paginator(current_page=page)
    keyboard.add(
        types.InlineKeyboardButton(
            text="◀️",
            callback_data='back_to_letters'
        )
    )
    await callback.message.edit_text(
        await messages.get_message('choose_employee_name'),
        reply_markup=keyboard
    )


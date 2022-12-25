import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram_inline_paginations.paginator import Paginator
from telegram_bot_calendar import LSTEP

from filters import ManagerCheck
from keyboards.keyboards import yes_no
from keyboards.manager import ManagerCallbacks
from loader import dp, staff, messages
from utils.my_calendar import ChangeDateCalendar


@dp.callback_query_handler(ManagerCheck(), text=ManagerCallbacks.staff.value)
async def select_employee(callback: types.CallbackQuery):
    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(
        types.InlineKeyboardButton(
            text="Добавить сотрудника",
            callback_data=f'manager_employee_add'
        )
    )
    inline_keyboard.add(
        types.InlineKeyboardButton(
            text="Удалить сотрудника",
            callback_data=f'manager_employee_delete'
        )
    )

    await callback.message.edit_text(
        await messages.get_message('manager_staff_menu'),
        reply_markup=inline_keyboard
    )


# Удаление работника
@dp.callback_query_handler(ManagerCheck(), text="manager_employee_delete")
async def select_employee(callback: types.CallbackQuery):
    all_employees = await staff.select_all_employees()
    letters_list = await all_employees.lastname_first_letters()
    inline_keyboard = types.InlineKeyboardMarkup(row_width=7)
    for letter in letters_list:
        inline_keyboard.insert(
            types.InlineKeyboardButton(
                text=letter,
                callback_data=f'manager_employee_letter={letter}'
            )
        )
    await callback.message.edit_text(
        await messages.get_message('choose_letter'),
        reply_markup=inline_keyboard
    )


@dp.callback_query_handler(Text(equals="manager_back_to_letters"))
async def back_select_employee(callback: types.CallbackQuery):
    all_employees = await staff.select_all_employees()
    letters_list = await all_employees.lastname_first_letters()
    inline_keyboard = types.InlineKeyboardMarkup(row_width=7)
    for letter in letters_list:
        inline_keyboard.insert(
            types.InlineKeyboardButton(
                text=letter,
                callback_data=f'manager_employee_letter={letter}'
            )
        )
    await callback.message.edit_text(
        await messages.get_message('choose_letter'),
        reply_markup=inline_keyboard
    )


@dp.callback_query_handler(Text(startswith='manager_employee_letter='))
async def choose_employee_by_letter(callback: types.CallbackQuery):
    letter = callback.data.split('=')[1]
    all_employees = await staff.select_all_employees()
    inline_keyboard = types.InlineKeyboardMarkup()
    for employee in all_employees:
        if employee.lastname[0] == letter:
            inline_keyboard.add(
                types.InlineKeyboardButton(
                    text=f"{str(employee)}",
                    callback_data=f"manageremployee={employee.id}"
                )
            )
    paginator = Paginator(inline_keyboard, callback_startswith=f'manageremployees_{letter}_')
    keyboard = paginator()
    keyboard.add(
        types.InlineKeyboardButton(
            text="◀️",
            callback_data='manager_back_to_letters'
        )
    )
    await callback.message.edit_text(
        await messages.get_message('choose_employee_name'),
        reply_markup=keyboard
    )


@dp.callback_query_handler(Text(startswith="manageremployees_"))
async def choose_employee_by_letter_page(callback: types.CallbackQuery):
    letter = callback.data.split("_")[1]
    page = int(callback.data.split("_")[2])

    all_employees = await staff.select_all_employees()
    inline_keyboard = types.InlineKeyboardMarkup()
    for employee in all_employees:
        if employee.lastname[0] == letter:
            inline_keyboard.add(
                types.InlineKeyboardButton(
                    text=f"{str(employee)}",
                    callback_data=f"manageremployee={employee.id}"
                )
            )
    paginator = Paginator(inline_keyboard, callback_startswith=f'manageremployees_{letter}_')
    keyboard = paginator(current_page=page)
    keyboard.add(
        types.InlineKeyboardButton(
            text="◀️",
            callback_data='manager_back_to_letters'
        )
    )
    await callback.message.edit_text(
        await messages.get_message('choose_employee_name'),
        reply_markup=keyboard
    )


@dp.callback_query_handler(Text(startswith="manageremployee="))
async def edit_employee(callback: types.CallbackQuery):
    employee_to_edit = int(callback.data.split("manageremployee=")[1])
    employee = await staff.select_employee(id=employee_to_edit)
    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(
        types.InlineKeyboardButton(
            text=f"🗑️{employee.full_name()}",
            callback_data=f"removeemployee={employee.id}",
        )
    )
    inline_keyboard.add(
        types.InlineKeyboardButton(
            text=f"Отмена",
            callback_data=ManagerCallbacks.staff.value,
        )
    )
    await callback.message.edit_text(
        f"{employee.info()}",
        reply_markup=inline_keyboard
    )


@dp.callback_query_handler(ManagerCheck(), Text(startswith="removeemployee="))
async def remove_employee(callback: types.CallbackQuery):
    employee_to_remove = int(callback.data.split("removeemployee=")[1])
    employee = await staff.select_employee(id=employee_to_remove)

    await staff.delete_employee(employee.id)
    logging.info(f"[{callback.message.from_user.id}] удалил [{employee=}]")

    await callback.message.edit_text(
        f"Сотрудник {employee.full_name()} успешно удалён из базы"
    )


# Добавление работника
class AddEmployee(StatesGroup):
    Name = State()
    Phone = State()
    Email = State()
    Birth = State()
    Confirm = State()


@dp.callback_query_handler(ManagerCheck(), text="manager_employee_add")
async def input_name(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Введи ФИО работника (можно без отчества если его нет):"
    )
    await AddEmployee.Name.set()


@dp.message_handler(state=AddEmployee.Name, content_types=types.ContentType.TEXT)
async def save_name(message: types.Message, state: FSMContext):
    words_count = len(message.text.split(" "))
    if 1 < words_count <= 3:
        async with state.proxy() as data:
            data['name'] = message.text
        await message.answer(
            "Введи номер телефона сотрудника в формате 79112223344:"
        )
        await AddEmployee.Phone.set()
    else:
        return await message.reply("Непонятное ФИО")


@dp.message_handler(state=AddEmployee.Phone, regexp=r'^(7)\(?[489][0-9]{2}\)?[0-9]{3}[0-9]{2}[0-9]{2}$')
async def save_phone(message: types.Message, state: FSMContext):
    check_exists = await staff.select_employee(phone=message.text)
    if not check_exists:
        async with state.proxy() as data:
            data['phone'] = message.text
        await message.answer(
            "Введи email сотрудника:"
        )
        await AddEmployee.Email.set()
    else:
        return await message.reply("Этот номер есть в базе")


@dp.message_handler(state=AddEmployee.Email, regexp=r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
async def save_email(message: types.Message, state: FSMContext):
    check_exists = await staff.select_employee(email=message.text)
    if not check_exists:
        async with state.proxy() as data:
            data['email'] = message.text
        calendar, step = ChangeDateCalendar(calendar_id=0).build()
        await message.answer(f"Выберите {LSTEP[step]} рождения сотрудника (год выбирать не нужно):", reply_markup=calendar)
        await AddEmployee.Birth.set()
    else:
        return await message.reply("Этот email есть в базе")


@dp.callback_query_handler(ChangeDateCalendar.func(calendar_id=0), state=AddEmployee.Birth)
async def inline_kb_answer_callback_handler(callback: types.CallbackQuery, state: FSMContext):
    result, key, step = ChangeDateCalendar(calendar_id=0).process(callback.data)
    logging.info(f"{result=}, {step=}")
    if step == 'y':
        return await callback.answer("Год выбирать не нужно", show_alert=True)
    if not result and key:
        await callback.message.edit_text(f"Выберите {LSTEP[step]} рождения сотрудника:", reply_markup=key)
    elif result:
        day_birth = str(result).split("-")[2]
        mount_birth = str(result).split("-")[1]
        async with state.proxy() as data:
            data['day_birth'] = day_birth
            data['mount_birth'] = mount_birth

        data = await state.get_data()

        await callback.message.answer(
            f"<b>Проверка вносимых сведений:</b>\n"
            f"ФИО: {data['name']}\n"
            f"Телефон: {data['phone']}\n"
            f"email: {data['email']}\n"
            f"День рождения: {data['day_birth']}\n"
            f"Месяц рождения: {data['mount_birth']}\n\n"
            f"Сохраняем?",
            reply_markup=yes_no
        )
        await AddEmployee.Confirm.set()


@dp.message_handler(state=AddEmployee.Confirm, text="Да")
async def save_employee_to_db(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if len(data['name'].split(" ")) == 2:
        lastname = data['name'].split(" ")[0]
        firstname = data['name'].split(" ")[1]
        middlename = None
    else:
        lastname = data['name'].split(" ")[0]
        firstname = data['name'].split(" ")[1]
        middlename = data['name'].split(" ")[2]

    new_employee = await staff.add_employee(
        firstname=firstname,
        lastname=lastname,
        middlename=middlename,
        phone=data['phone'],
        email=data['email'],
        day_birth=int(data['day_birth']),
        month_birth=int(data['mount_birth']),
    )
    logging.info(f"[{message.from_user.id}] добавил [{new_employee=}]")
    await message.reply(
        f"Сотрудник сохранен:\n{new_employee.info()}",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.finish()


@dp.message_handler(state=AddEmployee.Confirm, text="Нет")
async def save_employee_to_db(message: types.Message, state: FSMContext):
    await message.reply(
        f"Сохранение отменено.",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.finish()

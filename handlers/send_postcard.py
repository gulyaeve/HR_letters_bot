import io
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram_inline_paginations.paginator import Paginator

from filters import AuthCheck
from keyboards.categories import make_inline_categories
from keyboards.keyboards import request_submit
from keyboards.postcards_menu import PostcardMenu, PostcardSelector
from loader import dp, staff, messages, postcards, postcards_db
from utils.email_sender import send_email_photo
from utils.utilities import make_keyboard_list, get_bot_info


class Thanks(StatesGroup):
    TypeMessage = State()
    ChooseTemplate = State()
    SignUpPostcard = State()
    Confirm = State()


@dp.message_handler(AuthCheck(), commands=['send_postcard', 'say_thanks'])
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


@dp.message_handler(commands=['send_postcard'])
async def select_employee_no_auth(message: types.Message):
    await message.reply(await messages.get_message("auth_mention"))


@dp.callback_query_handler(Text(equals="back_to_letters"))
@dp.callback_query_handler(Text(equals="back_to_letters"), state="*")
async def back_select_employee(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
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
                    text=f"{str(employee)}",
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
    if callback.message.text:
        await callback.message.edit_text(
            await messages.get_message('choose_employee_name'),
            reply_markup=keyboard
        )
    else:
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
                    text=f"{str(employee)}",
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


@dp.callback_query_handler(Text(startswith="employee="))
async def input_text_to_postcard(callback: types.CallbackQuery, state: FSMContext):
    employee_to_sent = callback.data.split("employee=")[1]
    async with state.proxy() as data:
        data['employee_id_to_sent'] = employee_to_sent

    await callback.message.edit_text(
        await messages.get_message("input_text"),
    )
    await Thanks.TypeMessage.set()


@dp.message_handler(state=Thanks.TypeMessage, content_types=types.ContentType.TEXT)
async def type_thanks(message: types.Message, state: FSMContext):
    # await state.finish()
    message_to_send = message.text
    if message_to_send.__len__() > 300:
        return await message.answer(await messages.get_message("too_many_letters"))
    async with state.proxy() as data:
        data['message'] = message_to_send

    categories_list = await postcards.get_postcards_types()
    keyboard = await make_inline_categories(
        categories=categories_list,
        current_page=0
    )
    keyboard.add(
        types.InlineKeyboardButton(
            text="◀️",
            callback_data='back_to_letters'
        )
    )

    await message.answer(
        await messages.get_message("choose_category"),
        reply_markup=keyboard
    )
    await Thanks.ChooseTemplate.set()


@dp.callback_query_handler(Text(startswith='page_'), state=Thanks.ChooseTemplate)
@dp.callback_query_handler(Text(startswith=PostcardMenu.back.value), state=Thanks.ChooseTemplate)
async def category_other_page(callback: types.CallbackQuery, state: FSMContext):
    # await state.finish()
    page_n = 0
    if callback.data.startswith("page_"):
        page_n = int(callback.data.split("_")[1])
    categories_list = await postcards.get_postcards_types()
    keyboard = await make_inline_categories(categories_list, current_page=page_n)
    keyboard.add(
        types.InlineKeyboardButton(
            text="◀️",
            callback_data='back_to_letters'
        )
    )

    # if callback.message.text:
    #     await callback.message.edit_text(
    #         await messages.get_message("choose_category"),
    #         reply_markup=keyboard,
    #     )
    # else:
    await callback.message.delete()
    await callback.message.answer(
        await messages.get_message("choose_category"),
        reply_markup=keyboard,
    )


@dp.callback_query_handler(Text(startswith="category="), state=Thanks.ChooseTemplate)
@dp.callback_query_handler(Text(startswith="category="))
async def preview_chooser(callback: types.CallbackQuery, state: FSMContext):
    category = callback.data.split("category=")[1]
    images = await postcards.get_postcards_list_by_type(category)

    async with state.proxy() as data:
        data['pic'] = 0
        data['category'] = category

    # postcard = await postcards.get_preview(category, images[data['pic']])
    postcard = await postcards.get_postcard(data['message'], category, images[data['pic']])
    await callback.message.delete()
    await callback.message.answer_photo(postcard, reply_markup=PostcardSelector.postcards_menu)
    await Thanks.ChooseTemplate.set()


@dp.callback_query_handler(text=PostcardMenu.left.value, state=Thanks.ChooseTemplate)
async def send_prev_pic(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category = data['category']
    images = await postcards.get_postcards_list_by_type(category)
    idx = data['pic']
    new_idx = (idx - 1) % len(images)
    async with state.proxy() as data:
        data['pic'] = new_idx
    # postcard_preview = await postcards.get_preview(category, images[data['pic']])
    postcard = await postcards.get_postcard(data['message'], category, images[data['pic']])
    await callback.message.delete()
    await callback.message.answer_photo(
        postcard,
        reply_markup=PostcardSelector.postcards_menu
    )


@dp.callback_query_handler(text=PostcardMenu.right.value, state=Thanks.ChooseTemplate)
async def send_next_pic(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category = data['category']
    images = await postcards.get_postcards_list_by_type(category)
    idx = data['pic']
    new_idx = (idx + 1) % len(images)
    async with state.proxy() as data:
        data['pic'] = new_idx
    # postcard_preview = await postcards.get_preview(category, images[data['pic']])
    postcard = await postcards.get_postcard(data['message'], category, images[data['pic']])
    await callback.message.delete()
    await callback.message.answer_photo(
        postcard,
        reply_markup=PostcardSelector.postcards_menu
    )


# @dp.callback_query_handler(text=PostcardMenu.ok.value, state=Thanks.ChooseTemplate)
# async def send_postcard(callback: types.CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     category = data['category']
#     images = await postcards.get_postcards_list_by_type(category)
#
#     postcard = await postcards.get_postcard(
#         text=data["message"],
#         category=category,
#         template=images[data['pic']]
#     )
#     await callback.message.delete()
#     await callback.message.answer_photo(
#         postcard,
#         reply_markup=PostcardSelector.postcards_accept_menu
#     )


# @dp.callback_query_handler(text=PostcardMenu.decline.value, state=Thanks.ChooseTemplate)
# async def cancel_postcard(callback: types.CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     category = data['category']
#     images = await postcards.get_postcards_list_by_type(category)
#
#     postcard_preview = await postcards.get_preview(category, images[data['pic']])
#     await callback.message.delete()
#     await callback.message.answer_photo(
#         postcard_preview,
#         reply_markup=PostcardSelector.postcards_menu
#     )


@dp.callback_query_handler(text=PostcardMenu.ok.value, state=Thanks.ChooseTemplate)
async def accept_postcard(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['file_id'] = callback.message.photo[-1].file_id
    await callback.message.edit_reply_markup(None)
    await callback.message.delete()
    await callback.message.answer(await messages.get_message("postcard_check"))
    await callback.message.answer_photo(data['file_id'])
    await callback.message.answer(
        await messages.get_message("choose_sigh"),
        reply_markup=make_keyboard_list(['Подписать', 'Анонимно'])
    )
    await Thanks.SignUpPostcard.set()


@dp.message_handler(Text(equals='Анонимно'), state=Thanks.SignUpPostcard)
async def postcard_anonymous(message: types.Message, state: FSMContext):
    sender_id = 0
    async with state.proxy() as data:
        data['sender_id'] = sender_id
    await message.answer(await messages.get_message("final_confirm"), reply_markup=request_submit)
    await Thanks.Confirm.set()


@dp.message_handler(Text(equals='Подписать'), state=Thanks.SignUpPostcard)
async def postcard_no_anonymous(message: types.Message, state: FSMContext):
    sender = await staff.select_employee(telegram_id=message.from_user.id)
    async with state.proxy() as data:
        data['sender_id'] = sender.id
    await message.answer(await messages.get_message("final_confirm"), reply_markup=request_submit)
    await Thanks.Confirm.set()


@dp.message_handler(Text(equals="Отправить"), state=Thanks.Confirm)
async def send_or_safe_postcard(message: types.Message, state: FSMContext):
    data = await state.get_data()
    sender_id = data['sender_id']
    user_to_send = await staff.select_employee(id=int(data['employee_id_to_sent']))
    file = await dp.bot.download_file_by_id(data['file_id'])

    postcard = await postcards_db.insert_postcard(
        user_id_who_sent=sender_id,
        user_id_to_send=user_to_send.id,
        file_id=data['file_id'],
        raw_file=file.getbuffer().tobytes(),
    )
    logging.info(f"Postcard save to db {sender_id=} {user_to_send=} {data['file_id']=}")
    await push_postcard(postcard)
    logging.info(f"Postcard pushed {sender_id=} {user_to_send=} {data['file_id']=}")

    # if user_to_send['telegram_id'] is not None:
    #     try:
    #         await bot.send_photo(user_to_send['telegram_id'], data['file_id'],
    #                              caption=f"Вам отправлена анонимная благодарность")
    #         logging.info(f"Success send message [{message.from_user.id}] [{user_to_send['telegram_id']}]")
    #     except:
    #         logging.info(f"Failed send message [{message.from_user.id}] [{user_to_send['telegram_id']}]")
    # if user_to_send['email'] is not None:
    #     try:
    #         await send_email_photo(user_to_send['email'],
    #                                'Вам отправлена благодарность',
    #                                f'Вам отправлена анонимная благодарность.\n'
    #                                f'Хочешь получать и создавать спасибки в телеграм, авторизуйся здесь >> https://t.me/{me.username}/',
    #                                file.getbuffer().tobytes())
    #         logging.info(f"Success send email [{message.from_user.id}] [{user_to_send['email']}]")
    #     except:
    #         logging.info(f"Failed send email [{message.from_user.id}] [{user_to_send['email']}]")
    #
    await message.reply(await messages.get_message("postcard_sended"),
                        reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


async def push_postcard(postcard):
    logging.info(f"prepare {postcard.id=}")
    if postcard.user_id_who_sent != 0:
        user_who_send = await staff.select_employee(id=postcard.user_id_who_sent)
    else:
        user_who_send = None
    user_to_send = await staff.select_employee(id=postcard.user_id_to_sent)
    logging.info(f"{postcard.id=} {user_who_send=} {user_to_send=}")
    # if postcard.file_id:
    #     file = (await bot.download_file_by_id(postcard.file_id)).getbuffer().tobytes()
    # else:
    file = bytes(postcard.raw_file)
    # logging.info(f"{type(file)=}")
    me = await get_bot_info()
    logging.info(f"Try to send {postcard.id=}")
    if user_who_send:
        if user_to_send.telegram_id is not None:
            if not postcard.time_sended_telegram:
                try:
                    await dp.bot.send_photo(
                        user_to_send.telegram_id,
                        postcard.file_id if postcard.file_id is not None else io.BytesIO(postcard.raw_file),
                        caption=f"{user_who_send.full_name()} отправляет вам открытку"
                    )
                    logging.info(f"Success send message [{user_to_send.telegram_id}]")
                    await postcards_db.update_date_telegram_send(postcard.id)
                except:
                    logging.info(f"Failed send message [{user_to_send.telegram_id}] [{postcard.file_id}]")
            else:
                logging.info(f"[{postcard.id}] уже была отправлена {postcard.time_sended_telegram=}")
        if user_to_send.email is not None:
            if not postcard.time_sended_email:
                try:
                    await send_email_photo(
                        user_to_send.email,
                        'Вам отправлена открытка',
                        f"{user_who_send.full_name()} отправляет вам открытку.\n"
                        f"Хочешь получать и создавать спасибки в телеграм, "
                        f"авторизуйся здесь >> https://t.me/{me.username}/",
                        file
                    )
                    logging.info(f"Success send email [{user_to_send.email}]")
                    await postcards_db.update_date_email_send(postcard.id)
                except:
                    logging.info(f"Failed send email [{user_to_send.email}]")
            else:
                logging.info(f"[{postcard.id}] уже была отправлена {postcard.time_sended_email=}")
    else:
        if user_to_send.telegram_id is not None:
            if not postcard.time_sended_telegram:
                try:
                    await dp.bot.send_photo(
                        user_to_send.telegram_id,
                        postcard.file_id if postcard.file_id is not None else io.BytesIO(postcard.raw_file),
                        caption=f"Вам отправлена анонимная открытка"
                    )
                    logging.info(f"Success send message [{user_to_send.telegram_id}]")
                    await postcards_db.update_date_telegram_send(postcard.id)
                except:
                    logging.info(f"Failed send message [{user_to_send.telegram_id}] [{postcard.file_id}]")
            else:
                logging.info(f"[{postcard.id}] уже была отправлена {postcard.time_sended_telegram=}")
        if user_to_send.email is not None:
            if not postcard.time_sended_email:
                try:
                    await send_email_photo(
                        user_to_send.email,
                        'Вам отправлена открытка',
                        f'Вам отправлена анонимная открытка.\n'
                        f'Хочешь получать и создавать спасибки в телеграм, '
                        f'авторизуйся здесь >> https://t.me/{me.username}/',
                        file
                    )
                    logging.info(f"Success send email [{user_to_send.email}]")
                    await postcards_db.update_date_email_send(postcard.id)
                except:
                    logging.info(f"Failed send email [{user_to_send.email}]")
            else:
                logging.info(f"[{postcard.id}] уже была отправлена {postcard.time_sended_email=}")

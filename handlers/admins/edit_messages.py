from logging import log, INFO

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp
from aiogram.dispatcher.filters.state import StatesGroup, State

from keyboards.admin import AdminCallbacks
from loader import messages, dp


class TextMessages(StatesGroup):
    Types = State()
    Description = State()
    Content = State()
    Edit = State()
    SaveText = State()


@dp.callback_query_handler(text="text_type_back", state=TextMessages.Content)
@dp.callback_query_handler(text=AdminCallbacks.text_messages.value)
async def choose_type(callback: types.CallbackQuery, state: FSMContext):
    message_types = await messages.select_all_message_types()
    inline_keyboard = types.InlineKeyboardMarkup()
    for message_type in message_types:
        inline_keyboard.add(
            types.InlineKeyboardButton(message_type['message_type'],
                                       callback_data=f"message_type={message_type['id']}")
        )
    inline_keyboard.add(types.InlineKeyboardButton(text="◀️", callback_data="back_to_main_admin_menu"))
    await callback.message.edit_text("Выбери тип сообщения:", reply_markup=inline_keyboard)
    await TextMessages.Description.set()


@dp.callback_query_handler(text="text_back", state=TextMessages.Edit)
@dp.callback_query_handler(Regexp('message_type=([0-9]*)'), state=TextMessages.Description)
async def choose_description(callback: types.CallbackQuery, state: FSMContext):
    try:
        message_type_id = int(callback.data.split("=")[1])
        async with state.proxy() as data:
            data['message_type_id'] = message_type_id
    except:
        data = await state.get_data()
        message_type_id = data['message_type_id']
    messages_by_type = await messages.select_messages_by_type(message_type_id)
    inline_keyboard = types.InlineKeyboardMarkup()
    for unit in messages_by_type:
        inline_keyboard.add(
            types.InlineKeyboardButton(unit['description'],
                                       callback_data=f"message_unit={unit['id']}")
        )
    inline_keyboard.add(types.InlineKeyboardButton(text="◀️", callback_data="text_type_back"))
    await callback.message.edit_text("Выбери описание сообщения:", reply_markup=inline_keyboard)
    await TextMessages.Content.set()


@dp.callback_query_handler(Regexp('message_unit=([0-9]*)'), state=TextMessages.Content)
async def choose_content(callback: types.CallbackQuery, state: FSMContext):
    message_id = int(callback.data.split("=")[1])
    message_text = await messages.get_message_content_by_id(message_id)
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="◀️", callback_data="text_back"),
             types.InlineKeyboardButton(text="🖍", callback_data="text_edit")]
        ])
    async with state.proxy() as data:
        data['message_id'] = message_id
    await callback.message.edit_text(message_text, reply_markup=keyboard)
    await TextMessages.Edit.set()


@dp.callback_query_handler(text="text_edit", state=TextMessages.Edit)
async def edit_text(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введи новый текст:")
    await TextMessages.SaveText.set()


@dp.message_handler(state=TextMessages.SaveText)
async def save_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await messages.update_text_content(message.html_text, data['message_id'])
    log(INFO, f"Text edited [{message.html_text}]")
    await message.answer("Текст сохранён")
    await state.finish()


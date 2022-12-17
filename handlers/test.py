import io

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State

from keyboards.categories import make_inline_categories
from keyboards.postcards_menu import PostcardSelector, PostcardMenu
from loader import dp, postcards


class Thanks(StatesGroup):
    Search = State()
    TypeMessage = State()
    TypeMessage2 = State()
    TypeMessage2Confirm = State()
    ChooseTemplate = State()
    MakePostcard = State()
    SignUpPostcard = State()
    Confirm = State()
    ConfirmAnon = State()


@dp.message_handler(commands=['test'])
async def categories_buttons(message: types.Message):
    categories_list = await postcards.get_postcards_types()

    await message.answer(
        "Выбери категорию:",
        reply_markup=await make_inline_categories(
            categories=categories_list,
            current_page=0)
    )


@dp.callback_query_handler(Text(startswith='page_'))
@dp.callback_query_handler(Text(startswith=PostcardMenu.back.value), state=Thanks.ChooseTemplate)
async def category_other_page(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    page_n = 0
    if callback.data.startswith("page_"):
        page_n = int(callback.data.split("_")[1])
    categories_list = await postcards.get_postcards_types()

    if callback.message.text:
        await callback.message.edit_text(
            "Выбери категорию:",
            reply_markup=(await make_inline_categories(categories_list, current_page=page_n))
        )
    else:
        await callback.message.delete()
        await callback.message.answer(
            "Выбери категорию:",
            reply_markup=(await make_inline_categories(categories_list, current_page=page_n))
        )


@dp.callback_query_handler(Text(startswith="category="))
async def preview_chooser(callback: types.CallbackQuery, state: FSMContext):
    category = callback.data.split("category=")[1]
    images = await postcards.get_postcards_list_by_type(category)

    async with state.proxy() as data:
        data['pic'] = 0
        data['category'] = category

        # data['message'] = "TEST\nHELLO"

    postcard = await postcards.get_preview(category, images[data['pic']])
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
    postcard_preview = await postcards.get_preview(category, images[data['pic']])
    await callback.message.edit_media(
        types.InputMediaPhoto(types.InputFile(io.BytesIO(postcard_preview))),
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
    postcard_preview = await postcards.get_preview(category, images[data['pic']])
    await callback.message.edit_media(
        types.InputMediaPhoto(types.InputFile(io.BytesIO(postcard_preview))),
        reply_markup=PostcardSelector.postcards_menu
    )


@dp.callback_query_handler(text=PostcardMenu.ok.value, state=Thanks.ChooseTemplate)
async def send_postcard(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category = data['category']
    images = await postcards.get_postcards_list_by_type(category)

    # postcard = await make_postcard(data['message'], data['pic'], callback.from_user.id)
    postcard = await postcards.get_postcard(
        text=data["message"],
        category=category,
        template=images[data['pic']]
    )
    postcard_media = types.InputMediaPhoto(types.InputFile(io.BytesIO(postcard)))
    await callback.message.edit_media(
        postcard_media,
        reply_markup=PostcardSelector.postcards_accept_menu
    )


@dp.callback_query_handler(text=PostcardMenu.decline.value, state=Thanks.ChooseTemplate)
async def cancel_postcard(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category = data['category']
    images = await postcards.get_postcards_list_by_type(category)

    postcard_preview = await postcards.get_preview(category, images[data['pic']])
    await callback.message.edit_media(
        types.InputMediaPhoto(types.InputFile(io.BytesIO(postcard_preview))),
        reply_markup=PostcardSelector.postcards_menu
    )

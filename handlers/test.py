from aiogram import types

from loader import dp, postcards


@dp.message_handler(commands=['test'])
async def test(message: types.Message):
    # postcard = await make_postcard('test')
    # postcard = await get_file("postcard/?text=Привет, как дела?&category=say_thanks&template=picture0")
    postcard = await postcards.get_postcard("HELLO", "say_thanks", "picture2")
    await message.answer_photo(postcard)
    preview = await postcards.get_preview("say_thanks", "picture1")
    await message.answer_photo(preview)
    await message.answer(await postcards.get_postcards_types())
    await message.answer(await postcards.get_postcards_list_by_type("say_thanks"))

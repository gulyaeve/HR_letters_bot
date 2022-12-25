from aiogram import types

from filters import ManagerCheck
from keyboards.manager import ManagerCallbacks
from loader import dp


@dp.callback_query_handler(ManagerCheck(), text=ManagerCallbacks.postcards.value)
async def manager_postcard_start(callback: types.CallbackQuery):
    await callback.answer(
        "Этот раздел в доработке",
        show_alert=True
    )

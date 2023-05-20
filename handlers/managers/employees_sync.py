from aiogram import types

from filters import ManagerCheck
from handlers.managers.managers import notify_managers
from loader import dp
from utils.staff_from_confluence import make_sync
from utils.utilities import make_file


@dp.callback_query_handler(ManagerCheck(), text="manager_employee_sync")
async def sync_employees(callback: types.CallbackQuery):
    report = await make_sync()
    file = await make_file(report, "report.txt")
    await callback.message.answer_document(file)
    await notify_managers("Выполнена синхронизация базы и таблицы")
    await callback.answer("Выполнена синхронизация базы и таблицы", show_alert=True)

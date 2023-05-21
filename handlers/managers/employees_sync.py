import datetime
import io
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from filters import ManagerCheck
from handlers.admins.admins import file_to_admins, notify_admins
from handlers.managers.managers import notify_managers, file_to_managers
from loader import dp, users
from utils.staff_from_confluence import make_sync
from utils.utilities import make_file


class HRCsv(StatesGroup):
    HRGetCsv = State()


@dp.callback_query_handler(ManagerCheck(), text="manager_employee_sync")
async def start_sync_employees(callback: types.CallbackQuery):
    await callback.message.answer_photo(types.InputFile("static/csv_1.png"))
    await callback.message.answer_photo(types.InputFile("static/csv_2.png"))
    await callback.message.answer(
        "Пришли мне csv файл с данными сотрудников, экспортированный из confluence:"
    )
    await HRCsv.HRGetCsv.set()


@dp.message_handler(state=HRCsv.HRGetCsv, content_types=types.ContentType.DOCUMENT)
async def make_synchronization(message: types.Message, state: FSMContext):
    logging.info(f"{message.from_user.id} send {message.document.file_name}")
    if message.document.file_name.endswith(".csv"):
        current_datetime = datetime.datetime.now()
        user = await users.select_user(message.from_user.id)
        file_name = f"staff_{current_datetime}"
        await message.document.download(
            destination_file=f"temp/{file_name}.csv",
        )
        report = await make_sync(f"temp/{file_name}.csv")

        await notify_managers(f"{user.full_name} выполнил синхронизацию базы бота и таблицы confluence")
        await notify_admins(f"{user.full_name} выполнил синхронизацию базы бота и таблицы confluence")

        report_file = f"temp/report_{current_datetime}.txt"
        with open(report_file, "w") as file:
            file.write(report)
        await file_to_managers(report_file)
        await file_to_admins(report_file)

        await state.finish()
    else:
        return await message.answer("Мне нужен файл csv")


@dp.message_handler(state=HRCsv.HRGetCsv, content_types=types.ContentType.ANY)
async def sync_wrong_type(message: types.Message):
    return await message.answer("Мне нужен файл csv")
    # report = await make_sync()
    # file = await make_file(report, "report.txt")
    # await callback.message.answer_document(file)
    # await notify_managers("Выполнена синхронизация базы и таблицы")
    # await callback.answer("Выполнена синхронизация базы и таблицы", show_alert=True)

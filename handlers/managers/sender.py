import asyncio
from logging import log, INFO
from random import randint

from aiogram import types

from filters import ManagerCheck
from loader import postcards_db, bot, staff, dp
from utils.email_sender import send_email_photo
from utils.utilities import get_bot_info


async def sender_from_db():
    postcard_count = await postcards_db.count_postcards()
    log(INFO, f"{postcard_count=}")
    for item in range(postcard_count):
        await asyncio.sleep(randint(10, 15))
        postcard = await postcards_db.select_postcard(item + 1)
        log(INFO, f"{postcard.id=}")
        if postcard.user_id_who_sent != 0:
            user_who_send = await staff.select_employee(id=postcard.user_id_who_sent)
        else:
            user_who_send = None
        user_to_send = await staff.select_employee(id=postcard.user_id_to_sent)
        file = await bot.download_file_by_id(postcard.file_id)
        me = await get_bot_info()
        if user_who_send:
            if user_to_send.telegram_id is not None:
                try:
                    await bot.send_photo(
                        user_to_send.telegram_id,
                        postcard.file_id,
                        caption=f"{user_who_send.full_name()} отправляет вам благодарность"
                    )
                    log(INFO, f"Success send message [{user_to_send.telegram_id}]")
                except:
                    log(INFO, f"Failed send message [{user_to_send.telegram_id}] [{postcard.file_id}]")
            if user_to_send.email is not None:
                try:
                    await send_email_photo(
                        user_to_send.email,
                        'Вам отправлена благодарность',
                        f"{user_who_send.full_name()} отправляет вам благодарность.\n"
                        f"Хочешь получать и создавать спасибки в телеграм, "
                        f"авторизуйся здесь >> https://t.me/{me.username}/",
                        file.getbuffer().tobytes()
                    )
                    log(INFO, f"Success send email [{user_to_send.email}]")
                except:
                    log(INFO, f"Failed send email [{user_to_send.email}]")
        else:
            if user_to_send.telegram_id is not None:
                try:
                    await bot.send_photo(
                        user_to_send.telegram_id,
                        postcard.file_id,
                        caption=f"Вам отправлена анонимная благодарность"
                    )
                    log(INFO, f"Success send message [{user_to_send.telegram_id}]")
                except:
                    log(INFO, f"Failed send message [{user_to_send.telegram_id}] [{postcard.file_id}]")
            if user_to_send.email is not None:
                try:
                    await send_email_photo(
                        user_to_send.email,
                        'Вам отправлена благодарность',
                        f'Вам отправлена анонимная благодарность.\n'
                        f'Хочешь получать и создавать спасибки в телеграм, '
                        f'авторизуйся здесь >> https://t.me/{me.username}/',
                        file.getbuffer().tobytes()
                    )
                    log(INFO, f"Success send email [{user_to_send.email}]")
                except:
                    log(INFO, f"Failed send email [{user_to_send.email}]")


@dp.message_handler(ManagerCheck(), commands=['push_postcards'], run_task=True)
async def push_postcards(message: types.Message):
    await message.answer("Начинаю")
    await sender_from_db()
    await message.answer("Отправлено")

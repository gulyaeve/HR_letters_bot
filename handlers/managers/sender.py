import asyncio
import io
import random
from logging import log, INFO
from random import randint

from aiogram import types
from aiogram.dispatcher import FSMContext

from filters import ManagerCheck
from loader import postcards_db, bot, staff, dp, postcards
from utils.email_sender import send_email_photo
from utils.utilities import get_bot_info


async def sender_from_db():
    postcard_count = await postcards_db.count_postcards()
    log(INFO, f"{postcard_count=}")
    for item in range(postcard_count):
        await asyncio.sleep(randint(10, 15))
        postcard = await postcards_db.select_postcard(item + 1)
        log(INFO, f"prepare {postcard.id=}")
        if postcard.user_id_who_sent != 0:
            user_who_send = await staff.select_employee(id=postcard.user_id_who_sent)
        else:
            user_who_send = None
        user_to_send = await staff.select_employee(id=postcard.user_id_to_sent)
        log(INFO, f"{postcard.id=} {user_who_send=} {user_to_send=}")
        file_to_email: bytes
        # if postcard.file_id:
        #     file = (await bot.download_file_by_id(postcard.file_id)).getbuffer().tobytes()
        # else:
        file = bytes(postcard.raw_file)
        # log(INFO, f"{type(file)=}")
        me = await get_bot_info()
        log(INFO, f"Try to send {postcard.id=}")
        if user_who_send:
            if user_to_send.telegram_id is not None:
                if not postcard.time_sended_telegram:
                    try:
                        await bot.send_photo(
                            user_to_send.telegram_id,
                            postcard.file_id if postcard.file_id is not None else io.BytesIO(postcard.raw_file),
                            caption=f"{user_who_send.full_name()} отправляет вам открытку"
                        )
                        log(INFO, f"Success send message [{user_to_send.telegram_id}]")
                        await postcards_db.update_date_telegram_send(postcard.id)
                    except:
                        log(INFO, f"Failed send message [{user_to_send.telegram_id}] [{postcard.file_id}]")
                else:
                    log(INFO, f"[{postcard.id}] уже была отправлена {postcard.time_sended_telegram=}")
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
                        log(INFO, f"Success send email [{user_to_send.email}]")
                        await postcards_db.update_date_email_send(postcard.id)
                    except:
                        log(INFO, f"Failed send email [{user_to_send.email}]")
                else:
                    log(INFO, f"[{postcard.id}] уже была отправлена {postcard.time_sended_email=}")
        else:
            if user_to_send.telegram_id is not None:
                if not postcard.time_sended_telegram:
                    try:
                        await bot.send_photo(
                            user_to_send.telegram_id,
                            postcard.file_id if postcard.file_id is not None else io.BytesIO(postcard.raw_file),
                            caption=f"Вам отправлена анонимная открытка"
                        )
                        log(INFO, f"Success send message [{user_to_send.telegram_id}]")
                        await postcards_db.update_date_telegram_send(postcard.id)
                    except:
                        log(INFO, f"Failed send message [{user_to_send.telegram_id}] [{postcard.file_id}]")
                else:
                    log(INFO, f"[{postcard.id}] уже была отправлена {postcard.time_sended_telegram=}")
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
                        log(INFO, f"Success send email [{user_to_send.email}]")
                        await postcards_db.update_date_email_send(postcard.id)
                    except:
                        log(INFO, f"Failed send email [{user_to_send.email}]")
                else:
                    log(INFO, f"[{postcard.id}] уже была отправлена {postcard.time_sended_email=}")


@dp.message_handler(ManagerCheck(), commands=['push_postcards'])
@dp.async_task
async def push_postcards(message: types.Message):
    postcard_count = await postcards_db.count_postcards()
    await message.answer(f"Общее число открыток (отправленные и не отправленные) {postcard_count}, отправка начинается")
    await sender_from_db()
    await message.answer("Отправка завершена")


@dp.message_handler(ManagerCheck(), commands=['everybody_postcard'])
async def save_postcards_to_all(message: types.Message, state: FSMContext):
    await message.reply("Введи текст:")
    await state.set_state("EVERYBODY_POSTCARD")


@dp.message_handler(state="EVERYBODY_POSTCARD", content_types=types.ContentType.TEXT)
@dp.async_task
async def save_postcards_to_all_2(message: types.Message, state: FSMContext):
    text_to_save = message.text
    new_year_category: str = 'Новый год'
    images_names = await postcards.get_postcards_list_by_type(new_year_category)
    images = []
    for name in images_names:
        image = await postcards.get_postcard(
                    text=text_to_save,
                    category=new_year_category,
                    template=name,
                )
        images.append(image)

    all_employees = await staff.select_all_employees()

    await message.reply(
        f"Количество открыток: {len(images)}\n"
        f"Количество сотрудников: {len(all_employees)}\n"
        f"Начинаю сохранение открыток."
    )

    for employee in all_employees:
        await postcards_db.insert_postcard(
            user_id_who_sent=0,
            user_id_to_send=employee.id,
            file_id=None,
            raw_file=random.choice(images),
        )

    await message.answer("Открытки сохранены")
    await state.finish()


@dp.message_handler(ManagerCheck(), commands=['everybody_postcard_dir'])
async def save_postcards_to_all_dir(message: types.Message, state: FSMContext):
    await message.reply("Введи текст для открытки от директора:")
    await state.set_state("EVERYBODY_POSTCARD_DIR")


@dp.message_handler(state="EVERYBODY_POSTCARD_DIR", content_types=types.ContentType.TEXT)
@dp.async_task
async def save_postcards_to_all_dir_2(message: types.Message, state: FSMContext):
    text_to_save = message.text
    new_year_category: str = 'Новый год'
    image_name = 'picture1'
    image = await postcards.get_postcard(
        text=text_to_save,
        category=new_year_category,
        template=image_name,
    )

    all_employees = await staff.select_all_employees()

    await message.reply(
        f"Количество сотрудников: {len(all_employees)}\n"
        f"Начинаю сохранение открыток."
    )

    for employee in all_employees:
        await postcards_db.insert_postcard(
            user_id_who_sent=176,
            user_id_to_send=employee.id,
            file_id=None,
            raw_file=image,
        )

    await message.answer("Открытки сохранены")
    await state.finish()



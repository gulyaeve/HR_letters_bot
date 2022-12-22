import asyncio
from logging import log, INFO
from random import randint
from loader import postcards_db, bot, staff
from utils.email_sender import send_email_photo
from utils.utilities import get_bot_info

# list_of_ids = [68]


async def sender_from_db():
    postcard_count = await postcards_db.count_postcards()
    log(INFO, f"{postcard_count=}")
    for item in range(postcard_count):
        await asyncio.sleep(randint(10, 15))
        postcard = await postcards_db.select_postcard(item + 1)
        log(INFO, f"{postcard.id=}")
        user_who_send = await staff.select_employee(id=postcard.user_id_who_sent)
        user_to_send = await staff.select_employee(id=postcard.user_id_to_sent)
        file = await bot.download_file_by_id(postcard.file_id)
        me = await get_bot_info()
        if user_who_send is not None:
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
    # await notify_admins(f"Было отправлено {postcard_count} открыток")


# async def file_sender(file, message):
#     users_count = await db.count_users()
#     log(INFO, f"{users_count=}")
#     users = await db.select_all_users()
#     for user in users:
#         if user['id'] in list_of_ids:
#             await asyncio.sleep(randint(10, 15))
#             log(INFO, f"{user=}")
#             with open(file, "rb") as image:
#                 f = image.read()
#                 b = bytearray(f)
#             me = await get_bot_info()
#             if user is not None:
#                 if user['telegram_id'] is not None:
#                     try:
#                         message = message.replace(":-)", "🙂")
#                         await bot.send_photo(user['telegram_id'], b,
#                                              caption=f"{message}")
#                         log(INFO, f"Success send message [{user['telegram_id']}]")
#                     except:
#                         log(INFO, f"Failed send message [{user['telegram_id']}]")
#                 if user['email'] is not None:
#                     try:
#                         await send_email_photo(user['email'],
#                                                'Вам отправлена благодарность',
#                                                f'{message}.\n'
#                                                f'Хочешь получать и создавать спасибки в телеграм, авторизуйся здесь >> https://t.me/{me.username}/',
#                                                b)
#                         log(INFO, f"Success send email [{user['email']}]")
#                     except:
#                         log(INFO, f"Failed send email [{user['email']}]")
#         else:
#             log(INFO, f'current id [{user["id"]}] not in list')
#     await notify_admins(f"Открытка {file} была отправлена {users_count} пользователям")


# file1 = "sender_postcards/1.jpeg"
# file2 = "sender_postcards/2.jpeg"
# file3 = "sender_postcards/3.jpeg"
# file4 = "sender_postcards/4.jpeg"
# message4 = """
# Коллеги! Счастье - быть частью команды обра!! Эта команда сделала то, что спустя много лет до сих пор никто не может ни то что повторить, даже приблизится.
# Хотел сказать, что вы для меня не просто коллеги.. Кто-то из вас стал мне другом, кто-то - опытным наставником, у кого-то просто есть чему поучиться и перенять опыт. В нашей команде есть абсолютно все люди, окружив себя которыми, любой человек будет радоваться каждому дню на работе и любое дело по плечу.
# Вас стало так много, что уделить время и внимание каждому уже физически невозможно. Сегодня хочу сказать спасибо вам за то, что вы такие какие есть. Спасибо за профессионализм, за чувство плеча, за преданность и небезразличные к нашему общему делу.
# Желаю всем нам уверенности в своих силах и как можно раньше осознать , что ценность даже не в достижениях и благодарностях мэра и других начальников, а ценность в том, что ты можешь быть настоящим и самим собой в команде! В лучшей команде! А еще мы меняем город, надеюсь, к лучшему :-)
# --
# Евгений Комаренко"""



async def main():
    # await file_sender(file4, message4)
    await sender_from_db()
    # await file_sender(file1, 'Вам отправлена анонимная благодарность')
    # await file_sender(file2, 'Вам отправлена анонимная благодарность')
    # await file_sender(file3, 'Вам отправлена анонимная благодарность')
    # taskA = loop.create_task(sender_from_db())
    # taskB = loop.create_task(file_sender(file1, 'Вам отправлена анонимная благодарность'))
    # taskC = loop.create_task(file_sender(file2, 'Вам отправлена анонимная благодарность'))
    # taskD = loop.create_task(file_sender(file3, 'Вам отправлена анонимная благодарность'))
    # taskE = loop.create_task(file_sender(file4, message4))
    # await asyncio.wait([taskA, taskB, taskC, taskD, taskE])


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.close()
    except:
        pass

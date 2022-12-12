from logging import log, INFO

from aiogram import types

from aiogram.types import ContentType

from handlers.admins.admins import notify_admins
from handlers.managers.managers import copy_to_managers
from loader import dp, messages


@dp.message_handler(content_types=[ContentType.GROUP_CHAT_CREATED, ContentType.NEW_CHAT_MEMBERS])
async def add_to_groups(message: types.Message):
    await notify_admins(f"[{message.from_user.full_name}; @{message.from_user.username}; {message.from_user.id}]"
                        f" отправил: {message.content_type}\n"
                        f"id этой группы <code>{message.chat.id}</code>")


@dp.message_handler(content_types=ContentType.ANY)
async def content_handler(message: types.Message):
    """
    Any content handler
    """
    log(INFO, f"[{message.from_user.id=}] отправил: {message.content_type=}")
    await message.answer(await messages.get_message("welcome_help_hint"))
    # Отправка сообщения менеджерам
    await copy_to_managers(message)

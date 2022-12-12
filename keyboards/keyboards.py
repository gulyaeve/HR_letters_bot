from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

yes_no = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Да"),
            KeyboardButton(text="Нет")
        ],
    ],
    resize_keyboard=True
    )

choose_auth = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Email ✉️"),
            KeyboardButton(text="Номер ☎️", request_contact=True)
        ],
    ],
    resize_keyboard=True
    )

auth_phone = ReplyKeyboardMarkup(
    keyboard=[
        [
            # KeyboardButton(text="Email ✉️"),
            KeyboardButton(text="Отправить номер ☎️", request_contact=True)
        ],
    ],
    resize_keyboard=True
    )

request_submit = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отправить")
        ],
        [
            KeyboardButton(text="ОТМЕНА")
        ],
    ],
    resize_keyboard=True
    )


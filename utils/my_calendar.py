from telegram_bot_calendar import DetailedTelegramCalendar, MONTH


class ChangeDateCalendar(DetailedTelegramCalendar):
    prev_button = "◀️"
    next_button = "▶️"
    empty_nav_button = "Отмена"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.first_step = MONTH
        self.locale = 'ru'



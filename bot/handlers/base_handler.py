from aiogram import Dispatcher, Bot


class BaseHandler:
    def __init__(self, dp: Dispatcher, bot: Bot):
        self.dp = dp
        self.bot = bot

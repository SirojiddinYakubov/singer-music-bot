from aiogram import Bot, Dispatcher
from bot.core.config import settings
from bot.handlers.main_handler import MainHandler

bot = Bot(token=settings.TOKEN_API)
dp = Dispatcher()

main_handler = MainHandler(dp=dp, bot=bot)
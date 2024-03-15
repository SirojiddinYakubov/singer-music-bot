from aiogram import Bot, Dispatcher

from bot.core.config import settings
from bot.handlers import main_handler, music_handler

bot = Bot(token=settings.TOKEN_API, parse_mode="HTML")
dp = Dispatcher()

dp.include_routers(main_handler.router)
dp.include_routers(music_handler.router)
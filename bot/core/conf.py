from aiogram import Bot, Dispatcher

from bot.core.config import settings
from bot.handlers import main_handler
from bot.handlers import admin_music_handler
from bot.handlers import guest_music_handler

bot = Bot(token=settings.TOKEN_API, parse_mode="HTML")
dp = Dispatcher()

dp.include_routers(main_handler.router)
dp.include_routers(admin_music_handler.router)
dp.include_routers(guest_music_handler.router)
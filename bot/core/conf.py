from aiogram import Bot, Dispatcher
from bot.core.config import settings

bot = Bot(token=settings.TOKEN_API)
dp = Dispatcher()

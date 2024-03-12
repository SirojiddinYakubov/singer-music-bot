from aiogram import Bot, Dispatcher
from bot.config import settings

bot = Bot(token=settings.TOKEN_API)
dp = Dispatcher()
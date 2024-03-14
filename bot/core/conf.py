from aiogram import Bot, Dispatcher
from bot.core.config import settings
from bot.handlers.main_handler import MainHandler

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(url=str(settings.ASYNC_DATABASE_URI), echo=True)
sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

bot = Bot(token=settings.TOKEN_API, parse_mode="HTML")
dp = Dispatcher()

main_handler = MainHandler(dp=dp, bot=bot)
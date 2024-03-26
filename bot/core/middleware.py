from aiogram import Dispatcher, types
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware
from typing import Callable, Awaitable, Dict, Any, Optional
from babel import Locale
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select
from bot.models import User
from bot.core.db import async_session


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        # print("Incoming update:", event, data)
        async with self.session_pool() as session:
            data["session"] = session
            return await handler(event, data)


i18n = I18n(path="bot/locales", default_locale="uz", domain="messages")


class Localization(SimpleI18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        if Locale is None:  # pragma: no cover
            raise RuntimeError(
                f"{type(self).__name__} can be used only when Babel installed\n"
                "Just install Babel (`pip install Babel`) "
                "or aiogram with i18n support (`pip install aiogram[i18n]`)"
            )
        event_from_user: Optional[types.User] = data.get("event_from_user", None)
        if event_from_user is None:
            return "uz"
        async with async_session() as session:
            db_user = await session.execute(
                select(User).where(User.id == event_from_user.id)
            )
            db_user = db_user.scalar_one_or_none()
            if db_user:
                return db_user.lang_code
        return "uz"


i18n_middleware = Localization(i18n=i18n)


def register_middlewares(dp: Dispatcher):
    # dp.update.middleware(LoggingMiddleware())
    dp.update.middleware(DbSessionMiddleware(session_pool=async_session))
    dp.update.outer_middleware(i18n_middleware)

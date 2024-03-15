from aiogram import Dispatcher
from aiogram.utils.i18n import I18n, ConstI18nMiddleware
from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.core.db import sessionmaker

i18n = I18n(path="bot/locales", default_locale="uz", domain="messages")
i18n_middleware = ConstI18nMiddleware(i18n=i18n, locale="ru")


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
        async with self.session_pool() as session:
            data["session"] = session
            return await handler(event, data)


def register_middlewares(dp: Dispatcher):
    dp.update.outer_middleware(i18n_middleware)
    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))

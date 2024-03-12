from aiogram import types
from aiogram.exceptions import TelegramForbiddenError
from bot.config import settings


async def protect(func):
    """Custom decorator for admin-only access."""

    async def wrapper(message: types.Message, admin_id: int = settings.ADMIN_ID):
        if message.from_user.id != admin_id:
            raise TelegramForbiddenError("You are not authorized to use this command.")
        return await func(message)

    return wrapper

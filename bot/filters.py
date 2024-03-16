from aiogram.filters import Filter
from aiogram.types import Message

from bot.core.config import settings

class IsAdmin(Filter):
    def __init__(self, admin_ids: list = settings.ADMIN_IDS) -> None:
        self.admin_ids = admin_ids

    async def __call__(self, message: Message) -> bool:
        return self.admin_ids and int(message.from_user.id) in self.admin_ids

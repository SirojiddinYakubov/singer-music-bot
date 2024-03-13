from aiogram.filters import Filter
from aiogram.types import Message

from bot.core.config import settings

class IsAdmin(Filter):
    def __init__(self, admin_id: int | str = settings.ADMIN_ID) -> None:
        self.admin_id = admin_id

    async def __call__(self, message: Message) -> bool:
        return self.admin_id and int(message.from_user.id) == int(self.admin_id)

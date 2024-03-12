from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from bot.utils import protect


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Вы довольны своей работой?")


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("This is protected message!")
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from bot.core.middleware import GetAcceptLanguageMiddleware
from bot.filters import IsAdmin
from bot.core.babel import _

router = Router()
router.message.middleware(GetAcceptLanguageMiddleware())

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(_("Assalomu aleykum {full_name}!").format(full_name=message.from_user.full_name))


@router.message(Command("help"), IsAdmin())
async def cmd_help(message: Message):
    await message.answer("This is protected message!")
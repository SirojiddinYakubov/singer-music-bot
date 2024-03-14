from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from bot.filters import IsAdmin
from aiogram.utils.i18n import gettext as _

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(_("Assalomu aleykum"))
    # await message.answer(_("Assalomu aleykum {full_name}!").format(full_name=message.from_user.full_name))


@router.message(Command("help"), IsAdmin())
async def cmd_help(message: Message):
    await message.answer("This is protected message!")
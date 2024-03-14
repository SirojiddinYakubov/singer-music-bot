from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from bot.handlers.base_handler import BaseHandler
from bot.keyboards.main_keyboard import menu_keyboard

router = Router()


class MainHandler(BaseHandler):
    def __init__(self, *args, **kwargs):
        """ Register main handlers """
        super().__init__(*args, **kwargs)
        self.dp.message.register(self.start_command, CommandStart())

    async def start_command(self, message: types.Message, state: FSMContext):
        await message.answer(_("Assalomu aleykum"), reply_markup=menu_keyboard())

# @router.message(CommandStart())
# async def cmd_start(message: Message):
#     await message.answer(_("Assalomu aleykum"), reply_markup=menu_keyboard())
#     # await message.answer(_("Assalomu aleykum {full_name}!").format(full_name=message.from_user.full_name))
#
#
# @router.message(Command("help"), IsAdmin())
# async def cmd_help(message: Message):
#     await message.answer("This is protected message!")

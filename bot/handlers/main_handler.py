from aiogram import F, Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from bot.handlers.base_handler import BaseHandler
from bot.keyboards.guest.main_keyboard import guest_menu_keyboard
from bot.keyboards.admin.main_keyboard import admin_menu_keyboard
from bot.core.config import settings

router = Router()


class MainHandler(BaseHandler):
    def __init__(self, *args, **kwargs):
        """ Register main handlers """
        super().__init__(*args, **kwargs)
        self.dp.message.register(self.start_command, CommandStart())
        self.dp.message.register(self.upload_music, F.audio)

    async def start_command(self, message: types.Message, state: FSMContext):
        if message.from_user.id == int(settings.ADMIN_ID):
            await message.answer(_("Assalomu aleykum ADMIN"), reply_markup=admin_menu_keyboard())
        else:
            await message.answer(_("Assalomu aleykum {full_name}!").format(full_name=message.from_user.full_name), reply_markup=guest_menu_keyboard())

    async def upload_music(self, message: types.Message, state: FSMContext):
        print(27, message)
        print("Title:", message.audio.title)
        print("Duration:", message.audio.duration)
        print("File ID:", message.audio.file_id)
        print("Size:", message.audio.file_size)
        print("MIME Type:", message.audio.mime_type)
        await message.answer("Audio uploaded!")
    
# @router.message(CommandStart())
# async def cmd_start(message: Message):
#     await message.answer(_("Assalomu aleykum"), reply_markup=menu_keyboard())
#     # await message.answer(_("Assalomu aleykum {full_name}!").format(full_name=message.from_user.full_name))
#
#
# @router.message(Command("help"), IsAdmin())
# async def cmd_help(message: Message):
#     await message.answer("This is protected message!")

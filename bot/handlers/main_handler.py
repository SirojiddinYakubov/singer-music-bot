from aiogram import F, Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.base_handler import BaseHandler
from bot.keyboards.guest.main_keyboard import guest_menu_keyboard
from bot.keyboards.admin.main_keyboard import admin_menu_keyboard
from bot.core.config import settings
from bot.models import Music
from bot.utils import get_file_path

router = Router()


@router.message(CommandStart())
async def start_command(message: types.Message, session: AsyncSession, state: FSMContext):
    print(session)
    if message.from_user.id == int(settings.ADMIN_ID):
        await message.answer(_("Assalomu aleykum ADMIN"), reply_markup=admin_menu_keyboard())
    else:
        await message.answer(_("Assalomu aleykum {full_name}!").format(full_name=message.from_user.full_name),
                             reply_markup=guest_menu_keyboard())


@router.message(F.audio)
async def upload_music(message: types.Message, session: AsyncSession, state: FSMContext):
    path = await get_file_path(message.audio.file_id)
    music = Music(
        created_by=message.from_user.id,
        duration=message.audio.duration,
        file_id=message.audio.file_id,
        size=message.audio.file_size,
        mime_type=message.audio.mime_type,
        title=message.audio.file_name,
        path=path
    )
    session.add(music)
    await session.commit()
    await message.reply(_("Musiqa muvaffaqiyatli yuklandi!"))


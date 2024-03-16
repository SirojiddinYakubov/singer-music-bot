from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.guest.main_keyboard import guest_menu_kb
from bot.keyboards.admin.main_keyboard import admin_menu_kb
from bot.core.config import settings
from bot.models import Music
from bot.pagination import apply_pagination
from bot.utils import get_file_path

router = Router()


async def paginator(session: AsyncSession, page: int = 0):
    musics = await session.execute(select(Music))
    musics = musics.scalars().all()
    builder = InlineKeyboardBuilder()
    start_offset = page * 3
    limit = 2
    end_offset = start_offset + limit
    for music in musics[start_offset:end_offset]:
        builder.row(InlineKeyboardButton(text=f'👤 {music.title}'))
    buttons_row = []
    if page > 0:
        buttons_row.append(InlineKeyboardButton(text="⬅️"))
    if end_offset < len(musics):
        buttons_row.append(InlineKeyboardButton(text="➡️"))
    else:
        buttons_row.append(InlineKeyboardButton(text="➡️"))
    builder.row(*buttons_row)
    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='cancel'))
    return builder.as_markup()


@router.message(Command("help"))
async def start_command(message: types.Message, session: AsyncSession, state: FSMContext):
    # query = select(Music)
    # query, pagination = await apply_pagination(query, session, page_size=2, page_number=1)
    # response = await session.execute(query)
    # print(response.scalars().all())
    # print(pagination)
    print(await paginator(session=session, page=0))
    # await message.answer("Hello", reply_markup=await paginator(session=session, page=0))
    await message.answer("Hello")

import sys
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from bot.filters import IsAdmin
from bot.keyboards.admin.main_keyboard import admin_action_music_ikb
from bot.states.admin_states import AddMusicState, SearchMusicState
from bot.utils import get_file_path, handle_error, size_representation
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from bot.callbacks import MusicActionCallbackFactory, PaginatedMusicsCallbackFactory
from bot.core.config import settings
from bot.keyboards.base_keyboard import paginated_musics_ikb
from bot.models import Music
from bot.pagination import apply_pagination, calculate_start

router = Router()
@router.message(F.text, ~IsAdmin())
async def admin_search_music_result(
    message: types.Message, session: AsyncSession, state: FSMContext
):
    query = (
        select(Music)
        .filter(Music.title.ilike(f"%{message.text.lower()}%"))
        .order_by(desc(Music.created_at))
    )
    query, pagination = await apply_pagination(
        query, session, page_size=settings.PAGE_SIZE, page_number=1
    )
    response = await session.execute(query)

    text = f"🔍 {message.text}\n\n"
    await state.update_data(searched_text=message.text)

    musics = response.scalars().all()
    for i, music in enumerate(musics, start=1):
        text += f"{i}. {music.title}\n"
    else:
        text += _("{searched_text} bo'yicha qidiruvda hech qanday musiqa topilmadi!").format(searched_text=message.text)
    await message.reply(
        text, reply_markup=await paginated_musics_ikb(query, pagination, session)
    )
    
@router.callback_query(
    PaginatedMusicsCallbackFactory.filter(F.action.in_(["next", "prev"])), ~IsAdmin()
)
async def admin_callbacks_for_paginate(
    callback: types.CallbackQuery,
    callback_data: PaginatedMusicsCallbackFactory,
    session: AsyncSession,
    state: FSMContext,
):
    data = await state.get_data()
    searched_text = data.get("searched_text", None)
    query = select(Music).order_by(desc(Music.created_at))

    if searched_text:
        query = query.filter(Music.title.ilike(f"%{searched_text}%"))

    if callback_data.action == "next":
        if callback_data.page_number < callback_data.num_pages:
            page_number = callback_data.page_number + 1
        else:
            page_number = callback_data.page_number
            await callback.answer("This is the last page")
    elif callback_data.action == "prev":
        if callback_data.page_number > 1:
            page_number = callback_data.page_number - 1
        else:
            page_number = 1
            await callback.answer("This is the first page")
    query, pagination = await apply_pagination(
        query, session, page_size=callback_data.page_size, page_number=page_number
    )
    text = f"🔍 {searched_text}\n\n" if searched_text else ""
    response = await session.execute(query)
    musics = response.scalars().all()
    for i, music in enumerate(
        musics,
        start=calculate_start(pagination["page_number"], pagination["page_size"]),
    ):
        text += f"{i}. {music.title}\n"
    await callback.message.edit_text(text)
    await callback.message.edit_reply_markup(
        reply_markup=await paginated_musics_ikb(query, pagination, session)
    )
    await callback.answer()

@router.callback_query(
    PaginatedMusicsCallbackFactory.filter(F.action == "paginate"), ~IsAdmin()
)
async def admin_callbacks_for_music(
    callback: types.CallbackQuery,
    callback_data: PaginatedMusicsCallbackFactory,
    session: AsyncSession,
    state: FSMContext,
):
    await callback.message.answer(
        _("Qo'shiqni yuklab olish uchun avval to'lovni amalga oshiring!"),
    )
    await callback.answer()
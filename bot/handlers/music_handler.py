from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from bot.callbacks import PaginatedMusicsCallbackFactory
from bot.keyboards.guest.main_keyboard import paginated_musics_kb
from bot.models import Music
from bot.pagination import apply_pagination

router = Router()


@router.message(Command("help"))
async def help_command(
    message: types.Message, session: AsyncSession, state: FSMContext
):
    query = select(Music)
    query, pagination = await apply_pagination(
        query, session, page_size=5, page_number=1
    )
    response = await session.execute(query)
    text = f"🔍 {message.text}\n\n"
    for i, music in enumerate(response.scalars().all(), start=1):
        text += f"{i}. {music.title}\n"
    await message.reply(
        text, reply_markup=await paginated_musics_kb(query, pagination, session)
    )


@router.callback_query(PaginatedMusicsCallbackFactory.filter())
async def callbacks_for_musics_paginate(
    callback: types.CallbackQuery,
    callback_data: PaginatedMusicsCallbackFactory,
    session: AsyncSession,
):
    query = select(Music)
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
    
    response = await session.execute(query)
    text = "🔍 \n\n"
    start = (pagination["page_number"] * pagination["page_size"]) - 1 if pagination["page_number"] > 1 else 1
    for i, music in enumerate(response.scalars().all(), start=start):
        text += f"{i}. {music.title}\n"
        
    await callback.message.edit_text(text)    
    await callback.message.edit_reply_markup(
        "test", reply_markup=await paginated_musics_kb(query, pagination, session)
    )
    await callback.answer()

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from bot.callbacks import PaginatedMusicsCallbackFactory
from bot.core.config import settings
from bot.keyboards.guest.main_keyboard import paginated_musics_kb
from bot.models import Music
from bot.pagination import apply_pagination, calculate_start

router = Router()


@router.message(Command("help"))
async def help_command(
    message: types.Message, session: AsyncSession, state: FSMContext
):
    query = select(Music)
    query, pagination = await apply_pagination(
        query, session, page_size=settings.PAGE_SIZE, page_number=1
    )
    response = await session.execute(query)

    text = f"🔍 {message.text}\n\n"
    await state.update_data(search_header_text=text)
    for i, music in enumerate(response.scalars().all(), start=1):
        text += f"{i}. {music.title}\n"
    await message.reply(
        text, reply_markup=await paginated_musics_kb(query, pagination, session)
    )


@router.callback_query(
    PaginatedMusicsCallbackFactory.filter(F.action.in_(["next", "prev"]))
)
async def callbacks_for_paginate(
    callback: types.CallbackQuery,
    callback_data: PaginatedMusicsCallbackFactory,
    session: AsyncSession,
    state: FSMContext,
):
    data = await state.get_data()
    text = data.get("search_header_text", "")

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
    for i, music in enumerate(
        response.scalars().all(),
        start=calculate_start(pagination["page_number"], pagination["page_size"]),
    ):
        text += f"{i}. {music.title}\n"

    await callback.message.edit_text(text)
    await callback.message.edit_reply_markup(
        "test", reply_markup=await paginated_musics_kb(query, pagination, session)
    )
    await callback.answer()


@router.callback_query(PaginatedMusicsCallbackFactory.filter(F.action == "paginate"))
async def callbacks_for_music(
    callback: types.CallbackQuery,
    callback_data: PaginatedMusicsCallbackFactory,
    session: AsyncSession,
    state: FSMContext,
):
    music_id = callback_data.value
    query = select(Music).where(Music.id == music_id)
    response = await session.execute(query)
    db_music = response.scalar_one_or_none()
    if db_music:
        audio_file_id = db_music.file_id
        try:
            await callback.message.answer_audio(audio=audio_file_id)
        except Exception as e:
            print(f"Error sending audio: {e}")
            await callback.message.answer(_("Xatolik! Musiqa jo'natilmadi"))
    else:
        await callback.message.answer(_("Musiqa topilmadi!"))
    await callback.answer()

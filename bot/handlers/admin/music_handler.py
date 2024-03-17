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


@router.message(F.text == __("Qo'shiqlar ro'yhati 🎶"), IsAdmin())
async def admin_musics_list(
    message: types.Message, session: AsyncSession, state: FSMContext
):
    query = select(Music).order_by(desc(Music.created_at))
    query, pagination = await apply_pagination(
        query, session, page_size=settings.PAGE_SIZE, page_number=1
    )
    response = await session.execute(query)
    text = ""
    for i, music in enumerate(response.scalars().all(), start=1):
        text += f"{i}. {music.title}\n"
    await message.reply(
        text, reply_markup=await paginated_musics_ikb(query, pagination, session)
    )


@router.callback_query(
    PaginatedMusicsCallbackFactory.filter(F.action.in_(["next", "prev"])), IsAdmin()
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
    PaginatedMusicsCallbackFactory.filter(F.action == "paginate"), IsAdmin()
)
async def admin_callbacks_for_music(
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
        text = ""
        for col in ["title", "id", "duration", "size", "mime_type", "created_at", "created_by"]:
            if col == "size":
                text += f"{col}: {size_representation(db_music.size)}\n"
                continue
            text += f"{col}: {getattr(db_music, col)}\n"
        await callback.message.edit_text(text, reply_markup=await admin_action_music_ikb(db_music.id))
    else:
        await callback.message.answer(_("Musiqa topilmadi!"))
    await callback.answer()


@router.message(F.text == __("Qo'shiq izlash 🔎"), IsAdmin())
async def admin_search_musics(message: types.Message, state: FSMContext):
    await state.set_state(SearchMusicState.title)
    await message.answer(_("Qo'shiq yoki qo'shiqchi nomini kiriting!"))


@router.message(SearchMusicState.title, IsAdmin())
async def admin_search_music_result(
    message: types.Message, session: AsyncSession, state: FSMContext
):
    await state.clear()

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
    await message.reply(
        text, reply_markup=await paginated_musics_ikb(query, pagination, session)
    )


@router.message(F.text == __("Qo'shiq qo'shish ➕"), IsAdmin())
async def admin_add_music(message: types.Message, state: FSMContext):
    await state.set_state(AddMusicState.audio)
    await message.answer(_("Audio faylni yuklang!"))


@router.message(AddMusicState.audio, IsAdmin())
async def admin_upload_music(
    message: types.Message, session: AsyncSession, state: FSMContext
):
    await state.clear()

    path = await get_file_path(message.audio.file_id)
    music = Music(
        created_by_id=message.from_user.id,
        duration=message.audio.duration,
        file_id=message.audio.file_id,
        size=message.audio.file_size,
        mime_type=message.audio.mime_type,
        title=message.audio.file_name,
        path=path,
    )
    session.add(music)
    await session.commit()
    await message.reply(_("Musiqa muvaffaqiyatli yuklandi!"))

@router.callback_query(
    MusicActionCallbackFactory.filter(F.action == "download"), IsAdmin()
)
async def admin_download_music(
    callback: types.CallbackQuery,
    callback_data: MusicActionCallbackFactory,
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
            await handle_error(
                f"Error sending audio in '{__file__}'\nLinenumer: {sys._getframe().f_lineno}\nException: {e}",
                e,
            )
    else:
        await callback.message.answer(_("Musiqa topilmadi!"))
    await callback.answer()
    
    
@router.callback_query(
    MusicActionCallbackFactory.filter(F.action == "delete"), IsAdmin()
)
async def admin_delete_music(
    callback: types.CallbackQuery,
    callback_data: MusicActionCallbackFactory,
    session: AsyncSession,
    state: FSMContext,
):
    music_id = callback_data.value
    query = select(Music).filter(Music.id == music_id)
    result = await session.execute(query)
    music_obj = result.scalar_one_or_none()
    music_title = music_obj.title
    if music_obj:
        await session.delete(music_obj)
        await session.commit()
        print(f"Music file with id {music_id} deleted successfully.")
        await callback.message.delete()
        await callback.message.answer(_("{music_title} muvaffaqiyatli o'chirildi!").format(music_title=music_title))
    else:
        print(f"Music file with id {music_id} not found.")
    await callback.answer()
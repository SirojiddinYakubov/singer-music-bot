import os
import sys
import uuid

from aiogram import Router, types, F
from aiogram.enums import ChatAction
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from sqlalchemy import desc, select, asc
from sqlalchemy.ext.asyncio import AsyncSession

from bot.callbacks import MusicActionCallbackFactory, PaginatedMusicsCallbackFactory, PaginatedPurchasesCallbackFactory
from bot.core.config import settings
from bot.filters import IsAdmin
from bot.keyboards.admin.main_keyboard import admin_action_music_ikb
from bot.keyboards.base_keyboard import paginated_musics_ikb, paginated_purchases_ikb
from bot.models import Music, Purchase
from bot.pagination import apply_pagination, calculate_start
from bot.states.admin_states import AddMusicState, SearchMusicState
from bot.utils import size_representation, download_audio

router = Router()


@router.message(or_f(F.text == __("🎶 Qo'shiqlar ro'yhati"), Command('musics')), IsAdmin())
async def admin_musics_list(
        message: types.Message, session: AsyncSession, state: FSMContext
):
    await state.clear()
    query = select(Music).filter(Music.is_active.is_(True)).order_by(asc(Music.sort), desc(Music.created_at))
    query, pagination = await apply_pagination(
        query, session, page_size=settings.PAGE_SIZE, page_number=1
    )
    response = await session.execute(query)
    musics = response.scalars().all()
    if len(musics):
        text = ""
        for i, music in enumerate(musics, start=1):
            text += f"{i}. {music.title}\n"
    else:
        text = _("Qo'shiq topilmadi!")
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
    query = select(Music).filter(Music.is_active.is_(True)).order_by(asc(Music.sort), desc(Music.created_at))

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
    query = select(Music).where(Music.id == music_id, Music.is_active.is_(True))
    response = await session.execute(query)
    db_music = response.scalar_one_or_none()
    if db_music:
        text = ""
        for col in ["title", "id", "duration", "price", "size", "mime_type", "is_active", "sort", "created_at",
                    "created_by"]:
            if col == "size":
                text += f"{col}: {size_representation(db_music.size)}\n"
                continue
            text += f"{col}: {getattr(db_music, col)}\n"
        await callback.message.edit_text(text, reply_markup=await admin_action_music_ikb(db_music.id))
    else:
        await callback.message.answer(_("Qo'shiq topilmadi!"))
    await callback.answer()


@router.message(F.text == __("🔎 Qo'shiq izlash"), IsAdmin())
async def admin_search_musics(message: types.Message, state: FSMContext):
    await state.set_state(SearchMusicState.title)
    await message.answer(_("Qo'shiq nomini kiriting!"))


@router.message(SearchMusicState.title, IsAdmin())
async def admin_search_music_result(
        message: types.Message, session: AsyncSession, state: FSMContext
):
    await state.clear()
    query = (
        select(Music)
        .filter(Music.is_active.is_(True))
        .filter(Music.title.ilike(f"%{message.text.lower()}%"))
        .order_by(desc(Music.created_at))
    )
    query, pagination = await apply_pagination(
        query, session, page_size=settings.PAGE_SIZE, page_number=1
    )
    response = await session.execute(query)
    await state.update_data(searched_text=message.text)

    musics = response.scalars().all()
    if len(musics):
        text = f"🔍 {message.text}\n\n"
        for i, music in enumerate(musics, start=1):
            text += f"{i}. {music.title}\n"
    else:
        text = _("{searched_text} bo'yicha qidiruvda hech qanday qo'shiq topilmadi!").format(searched_text=message.text)
    await message.reply(
        text, reply_markup=await paginated_musics_ikb(query, pagination, session)
    )


@router.message(F.text == __("➕ Qo'shiq qo'shish"), IsAdmin())
async def admin_add_music(message: types.Message, state: FSMContext):
    await state.set_state(AddMusicState.audio)
    await message.answer(_("Audio faylni yuklang!"))


@router.message(AddMusicState.audio, F.audio, IsAdmin())
async def admin_upload_music(
        message: types.Message, state: FSMContext, session: AsyncSession
):
    try:
        if not message.audio.mime_type.startswith('audio/mpeg'):
            raise Exception(_("Kechirasiz, faqat MP3 formatidagi qo'shiq fayllariga ruxsat beriladi."))

        # Download the audio file to the local media folder
        file_id = message.audio.file_id
        file_path = f"musics/{uuid.uuid4()}.mp3"
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)

        await message.bot.send_chat_action(
            chat_id=message.chat.id, action=ChatAction.TYPING
        )

        await download_audio(file_id, full_path)

        music = Music(
            created_by_id=message.from_user.id,
            duration=message.audio.duration,
            size=message.audio.file_size,
            mime_type=message.audio.mime_type,
            title=message.audio.file_name,
            path=file_path,
            is_active=False
        )
        session.add(music)
        await session.commit()

        await state.set_state(AddMusicState.price)
        await state.update_data(music_id=music.id)
        await message.reply(_("Endi qo'shiq narxini UZS'da kiriting: Masalan: 200000"))
    except Exception as e:
        print(e)
        return await message.reply(str(e))


@router.message(AddMusicState.audio, ~F.audio, IsAdmin())
async def admin_upload_music(message: types.Message):
    await message.reply(_("Iltimos, audio faylni yuklang!"))


@router.message(AddMusicState.price, F.text.isdigit(), IsAdmin())
async def admin_set_music_price(
        message: types.Message, session: AsyncSession, state: FSMContext
):
    try:
        data = await state.get_data()
        if data and "music_id" not in data:
            raise Exception(_("Oldin yuklangan qo'shiq topilmadi!"))

        query = select(Music).where(Music.id == int(data["music_id"]))
        response = await session.execute(query)
        db_music = response.scalar_one_or_none()
        if not db_music:
            raise Exception(_("Oldin yuklangan qo'shiq topilmadi!"))
        db_music.price = int(message.text)
        session.add(db_music)
        await session.commit()

        await state.set_state(AddMusicState.sort)
        await message.reply(_("Endi qo'shiq tartibini kiriting: Masalan: 1"))
    except Exception as e:
        print(e)
        return await message.reply(str(e))


@router.message(AddMusicState.price, ~F.text.isdigit(), IsAdmin())
async def admin_set_music_price(message: types.Message):
    await message.reply(_("Narx kiritishda xatolik! Quyidagi formatda kiriting: Masalan: 200000"))


@router.message(AddMusicState.sort, F.text.isdigit(), IsAdmin())
async def admin_set_music_sort(
        message: types.Message, session: AsyncSession, state: FSMContext
):
    try:
        data = await state.get_data()
        if data and "music_id" not in data:
            raise Exception(_("Oldin yuklangan qo'shiq topilmadi!"))

        query = select(Music).where(Music.id == int(data["music_id"]))
        response = await session.execute(query)
        db_music = response.scalar_one_or_none()
        if not db_music:
            raise Exception(_("Oldin yuklangan qo'shiq topilmadi!"))
        db_music.sort = int(message.text)
        db_music.is_active = True
        session.add(db_music)
        await session.commit()

        query = (
            select(Music)
            .filter(
                Music.is_active.is_(True),
                Music.id != int(db_music.id)
            ).order_by(
                asc(Music.sort),
                desc(Music.created_at)
            )
        )
        response = await session.execute(query)
        musics = response.scalars().all()
        if len(musics):
            for i, music in enumerate(musics, start=db_music.sort + 1):
                music.sort = i
                session.add(music)
            await session.commit()

        await state.clear()
        await message.reply(_("Jarayon muvaffaqiyatli amalga oshirildi!"))

    except Exception as e:
        print(e)
        return await message.reply(str(e))


@router.message(AddMusicState.sort, ~F.text.isdigit(), IsAdmin())
async def admin_set_music_sort(message: types.Message):
    await message.reply(_("Qo'shiq tartibini kiritishda xatolik! Quyidagi formatda kiriting: Masalan: 1"))


@router.callback_query(
    MusicActionCallbackFactory.filter(F.action == "download"), IsAdmin()
)
async def admin_download_music(
        callback: types.CallbackQuery,
        callback_data: MusicActionCallbackFactory,
        session: AsyncSession,
        state: FSMContext,
):
    try:
        music_id = callback_data.value
        query = select(Music).where(Music.id == music_id, Music.is_active.is_(True))
        response = await session.execute(query)
        db_music = response.scalar_one_or_none()
        if not db_music:
            raise Exception(_("Qo'shiq topilmadi!"))

        file_path = os.path.join(settings.MEDIA_ROOT, db_music.path)

        if not os.path.exists(file_path):
            raise Exception(
                f"Audio file not found in '{__file__}'\nLinenumer: {sys._getframe().f_lineno}"
            )

        await callback.message.bot.send_chat_action(
            chat_id=callback.message.chat.id, action=ChatAction.UPLOAD_DOCUMENT
        )

        await callback.message.reply_audio(
            audio=types.FSInputFile(
                path=file_path,
                filename=db_music.title
            ),
            protect_content=True
        )
        await callback.answer()
    except Exception as e:
        await callback.message.answer(str(e))

    # if db_music:
    #     audio_file_id = db_music.file_id
    #     try:
    #         await callback.message.answer_audio(audio=audio_file_id, protect_content=True)
    #     except Exception as e:
    #         await handle_error(
    #             f"Error sending audio in '{__file__}'\nLinenumer: {sys._getframe().f_lineno}\nException: {e}",
    #             e,
    #         )
    # else:
    #     await callback.message.answer(_("Qo'shiq topilmadi!"))
    # await callback.answer()


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
    query = select(Music).filter(Music.id == music_id, Music.is_active.is_(True))
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


@router.message(F.text == __("🎵 Sotib olingan qo'shiqlar"), IsAdmin())
async def admin_purchase_list(
        message: types.Message, session: AsyncSession, state: FSMContext
):
    await state.clear()
    query = (
        select(Purchase)
        .order_by(desc(Purchase.created_at))
    )
    query, pagination = await apply_pagination(
        query, session, page_size=settings.PAGE_SIZE, page_number=1
    )
    response = await session.execute(query)
    purchases = response.scalars().all()
    if len(purchases):
        text = ""
        for i, purchase in enumerate(purchases, start=1):
            text += f"{i}. {purchase.user} | {purchase.amount} so'm | {purchase.music.title} | {purchase.created_at}\n"
    else:
        text = _("Sotib olingan qo'shiqlar mavjud emas!")
    await message.reply(
        text, reply_markup=await paginated_purchases_ikb(query, pagination, session)
    )


@router.callback_query(
    PaginatedPurchasesCallbackFactory.filter(F.action.in_(["purchase_next", "purchase_prev"])), IsAdmin()
)
async def admin_purchase_callbacks_for_paginate(
        callback: types.CallbackQuery,
        callback_data: PaginatedPurchasesCallbackFactory,
        session: AsyncSession,
        state: FSMContext,
):
    query = select(Purchase).order_by(desc(Purchase.created_at))

    if callback_data.action == "purchase_next":
        if callback_data.page_number < callback_data.num_pages:
            page_number = callback_data.page_number + 1
        else:
            page_number = callback_data.page_number
            await callback.answer("This is the last page")
    elif callback_data.action == "purchase_prev":
        if callback_data.page_number > 1:
            page_number = callback_data.page_number - 1
        else:
            page_number = 1
            await callback.answer("This is the first page")
    query, pagination = await apply_pagination(
        query, session, page_size=callback_data.page_size, page_number=page_number
    )
    response = await session.execute(query)
    purchases = response.scalars().all()
    if len(purchases):
        text = ""
        for i, purchase in enumerate(
                purchases,
                start=calculate_start(pagination["page_number"], pagination["page_size"]),
        ):
            text += f"{i}. {purchase.user} | {purchase.amount} so'm | {purchase.music.title} | {purchase.created_at}\n"
    else:
        text = _("Sotib olingan qo'shiqlar mavjud emas!")
    await callback.message.edit_text(text)
    await callback.message.edit_reply_markup(
        reply_markup=await paginated_purchases_ikb(query, pagination, session)
    )
    await callback.answer()


@router.callback_query(
    MusicActionCallbackFactory.filter(F.action == "edit"), IsAdmin()
)
async def admin_edit_music(
        callback: types.CallbackQuery,
        callback_data: MusicActionCallbackFactory,
        state: FSMContext,
):
    try:
        music_id = callback_data.value
        await state.set_state(AddMusicState.price)
        await state.update_data(music_id=music_id)
        await callback.message.answer(_("Endi qo'shiq narxini UZS'da kiriting: Masalan: 200000"))
    except Exception as e:
        print(e)
        return await callback.message.answer(str(e))

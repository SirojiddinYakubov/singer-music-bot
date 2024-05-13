import sys
from aiogram import Router, types, F
from aiogram.enums import ContentType
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.i18n import lazy_gettext as __
from bot.callbacks import PaginatedMusicsCallbackFactory, PaymentInfoFactory
from bot.core.config import settings
from bot.filters import IsAdmin
from bot.keyboards.base_keyboard import paginated_musics_ikb
from bot.models import Music, Purchase, User
from bot.pagination import apply_pagination, calculate_start
from bot.utils import handle_error

router = Router()


@router.message(or_f(F.text == __("🎶 Qo'shiqlar ro'yhati"), Command('musics')), ~IsAdmin())
async def admin_musics_list(
        message: types.Message, session: AsyncSession, state: FSMContext
):
    await state.clear()
    query = select(Music).order_by(desc(Music.created_at))
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


@router.message(F.text == __("🎵 Sotib olingan qo'shiqlar"), ~IsAdmin())
async def guest_purchase_list(
        message: types.Message, session: AsyncSession, state: FSMContext
):
    await state.clear()
    query = (
        select(Music)
        .join(Purchase, Purchase.music_id == Music.id)
        .filter(Purchase.user_id == message.from_user.id, Purchase.music_id == Music.id)
        .order_by(desc(Music.created_at))
    )
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


# @router.message(F.text, ~IsAdmin())
# async def admin_search_music_result(
#         message: types.Message, session: AsyncSession, state: FSMContext
# ):
#     query = (
#         select(Music)
#         .filter(Music.title.ilike(f"%{message.text.lower()}%"))
#         .order_by(desc(Music.created_at))
#     )
#     query, pagination = await apply_pagination(
#         query, session, page_size=settings.PAGE_SIZE, page_number=1
#     )
#     response = await session.execute(query)
#
#     await state.update_data(searched_text=message.text)
#
#     musics = response.scalars().all()
#     if len(musics):
#         text = f"🔍 {message.text}\n\n"
#         for i, music in enumerate(musics, start=1):
#             text += f"{i}. {music.title}\n"
#     else:
#         text = _("{searched_text} bo'yicha qidiruvda hech qanday qo'shiq topilmadi!").format(searched_text=message.text)
#     await message.reply(
#         text, reply_markup=await paginated_musics_ikb(query, pagination, session)
#     )


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
async def guest_callbacks_for_music(
        callback: types.CallbackQuery,
        callback_data: PaginatedMusicsCallbackFactory,
        session: AsyncSession,
        state: FSMContext,
):
    music_id = callback_data.value
    query = select(Music).where(Music.id == music_id)
    response = await session.execute(query)
    db_music = response.scalar_one_or_none()

    query = select(Purchase).where(
        Purchase.user_id == callback.from_user.id, Purchase.music_id == music_id
    )
    response = await session.execute(query)
    purchase = response.scalar_one_or_none()
    if purchase:
        audio_file_id = db_music.file_id
        try:
            return await callback.message.answer_audio(audio=audio_file_id, protect_content=True)
        except Exception as e:
            return await handle_error(
                f"Error sending audio in '{__file__}'\nLinenumer: {sys._getframe().f_lineno}\nException: {e}",
                e,
            )

    if not db_music:
        await callback.message.answer(_("Qo'shiq topilmadi!"))
        return
    music_price = db_music.price * 100
    await callback.message.bot.send_invoice(
        callback.message.chat.id,
        title=db_music.title,
        description="{music_title} !".format(music_title=db_music.title),
        provider_token=settings.PAYMENTS_PROVIDER_TOKEN,
        currency='UZS',
        # photo_url="https://www.gstatic.com/webp/gallery/1.jpg",
        # photo_height=512,  # !=0/None, иначе изображение не покажется
        # photo_width=512,
        # photo_size=512,
        is_flexible=False,  # True если конечная цена зависит от способа доставки
        prices=[types.LabeledPrice(label='Narxi', amount=music_price)],
        start_parameter='time-machine-example',
        payload=PaymentInfoFactory(user_id=callback.from_user.id, music_id=music_id,
                                   amount=music_price).pack(),
    )
    await callback.answer()


@router.pre_checkout_query(~IsAdmin())
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    print("Received pre-checkout query:", pre_checkout_query)
    await pre_checkout_query.answer(ok=True)


@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT, ~IsAdmin())
async def process_successful_payment(message: types.Message, session: AsyncSession):
    print('successful_payment:', message.successful_payment)
    payload = PaymentInfoFactory.unpack(message.successful_payment.invoice_payload)
    print(payload)
    purchase = Purchase(user_id=payload.user_id, music_id=payload.music_id, amount=payload.amount / 100)
    session.add(purchase)
    await session.commit()

    query = select(Music).where(Music.id == payload.music_id)
    response = await session.execute(query)
    db_music = response.scalar_one_or_none()
    if db_music:
        audio_file_id = db_music.file_id
        try:
            await message.answer_audio(audio=audio_file_id, protect_content=True)
        except Exception as e:
            await handle_error(
                f"Error sending audio in '{__file__}'\nLinenumer: {sys._getframe().f_lineno}\nException: {e}",
                e,
            )
    else:
        await handle_error(
            f"Music with id {payload.music_id} not found in '{__file__}'\nLinenumer: {sys._getframe().f_lineno}"
        )
        await message.answer(_("Qo'shiq topilmadi!"))

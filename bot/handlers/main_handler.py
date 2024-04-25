from aiogram import Router, types, F
from aiogram.filters import CommandStart, or_f
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from sqlalchemy.ext.asyncio import AsyncSession

from bot.callbacks import LangCallbackFactory
from bot.core.config import settings
from bot.helpers.main_helper import detect_user_language, set_user_language
from bot.keyboards.admin.main_keyboard import admin_menu_kb
from bot.keyboards.guest.main_keyboard import guest_menu_kb, ask_lang_code_kb

router = Router()


@router.message(CommandStart())
async def start_command(
        message: types.Message, session: AsyncSession, state: FSMContext
):
    lang_code = await detect_user_language(message.from_user, session)
    if not lang_code:
        return await message.answer(
            "Tilni tanlang:\nВыберите язык:", reply_markup=ask_lang_code_kb()
        )
    if message.from_user.id in settings.ADMIN_IDS:
        await message.answer(
            _("Assalomu aleykum ADMIN"), reply_markup=admin_menu_kb()
        )
    else:
        text = _("""
        Assalomu aleykum {full_name}! Menu orqali kerakli tanlovni tanlang:
        """).format(
            full_name=message.from_user.full_name
        )
        await message.answer(
            text,
            reply_markup=guest_menu_kb(),
        )


@router.callback_query(LangCallbackFactory.filter())
async def set_user_lang_callback(
        callback: types.CallbackQuery,
        callback_data: LangCallbackFactory,
        session: AsyncSession,
):
    lang_code = callback_data.value
    await set_user_language(callback.from_user, lang_code, session)
    await callback.message.delete()
    await callback.message.answer(
        "Til muvaffaqiyatli sozlandi!/Язык успешно установлен!",
    )
    await callback.answer()


@router.message(F.text == __("🌐 Tilni sozlash"))
async def set_user_lang(
        message: types.Message
):
    await message.answer(
        "Tilni tanlang:\nВыберите язык:", reply_markup=ask_lang_code_kb()
    )

from aiogram import F, Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession
from bot.callbacks import LangCallbackFactory
from bot.helpers.main_helper import detect_user_language, set_user_language
from bot.keyboards.guest.main_keyboard import guest_menu_kb, ask_lang_code_kb
from bot.keyboards.admin.main_keyboard import admin_menu_kb
from bot.core.config import settings
from bot.models import Music
from bot.utils import get_file_path

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
        Assalomu aleykum {full_name}!\n\nQidiruvni amalga oshirish uchun qo'shiq nomi yoki qo'shiqchi nomini kiriting
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
    if callback_data.action == "set":
        lang_code = callback_data.value
        await set_user_language(callback.from_user, lang_code, session)
        await callback.message.delete()
        await callback.message.answer(
            "Til muvaffaqiyatli sozlandi!/Язык успешно установлен!\n\nQidiruvni amalga oshirish uchun qo'shiq nomi yoki qo'shiqchi nomini kiriting/Введите название песни или имя исполнителя",
        )
    else:
        await callback.message.answer(
            "Tilni tanlang:\nВыберите язык:", reply_markup=ask_lang_code_kb()
        )
    await callback.answer()




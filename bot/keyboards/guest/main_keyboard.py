from aiogram import types
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callbacks import LangCallbackFactory

def guest_menu_kb():
    kb = [
        [
            types.KeyboardButton(text=_("Qo'shiqlar ro'yhati 🎶")),
            types.KeyboardButton(text=_("Qo'shiq izlash 🔎"))
        ],
    ]
    return types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder=_("Kerakli amalni tanlang")
    )


def ask_lang_code_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="O'zbek tili 🇺🇿", callback_data=LangCallbackFactory(action="set", value="uz")
    )
    builder.button(
        text="Rus tili 🇷🇺", callback_data=LangCallbackFactory(action="set", value="ru")
    )
    return builder.as_markup()
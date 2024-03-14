from aiogram import types
from aiogram.utils.i18n import gettext as _


def menu_keyboard():
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

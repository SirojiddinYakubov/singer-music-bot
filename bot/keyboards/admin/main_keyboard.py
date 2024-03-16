from aiogram import types
from aiogram.utils.i18n import gettext as _


def admin_menu_kb():
    kb = [
        [
            types.KeyboardButton(text=_("Qo'shiqlar ro'yhati 🎶"))
        ],
        [
            types.KeyboardButton(text=_("Qo'shiq izlash 🔎"))    
        ],
        [
            types.KeyboardButton(text=_("Qo'shiq qo'shish ")),
        ],
        [
            types.KeyboardButton(text=_("Sotib olingan qo'shiqlar ro'yhati")),
        ]
    ]
    return types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder=_("Kerakli amalni tanlang"),
    )

from aiogram import types
from aiogram.utils.i18n import gettext as _

from bot.callbacks import MusicActionCallbackFactory


def admin_menu_kb():
    kb = [
        [
            types.KeyboardButton(text=_("Qo'shiqlar ro'yhati 🎶"))
        ],
        [
            types.KeyboardButton(text=_("Qo'shiq izlash 🔎"))    
        ],
        [
            types.KeyboardButton(text=_("Qo'shiq qo'shish ➕")),
        ],
        [
            types.KeyboardButton(text=_("Sotib olingan qo'shiqlar ro'yhati 🎵")),
        ]
    ]
    return types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder=_("Kerakli amalni tanlang"),
    )


async def admin_action_music_ikb(music_id: int):
    buttons = [
        [
            types.InlineKeyboardButton(text=_("Yuklab olish 🎧"), callback_data=MusicActionCallbackFactory(action="download", value=music_id).pack()),
            types.InlineKeyboardButton(text=_("O'chirish ❌"), callback_data=MusicActionCallbackFactory(action="delete", value=music_id).pack()),
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
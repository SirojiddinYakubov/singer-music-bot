from aiogram import types
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callbacks import LangCallbackFactory, PaginatedMusicsCallbackFactory
from bot.pagination import calculate_start

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



# async def paginated_musics_kb(query, pagination, session):
#     builder = InlineKeyboardBuilder()
#     builder.max_width = 2
#     response = await session.execute(query)
#     musics_list = response.scalars().all()
#     print(pagination)
#     start = (pagination["page_number"] * pagination["page_size"]) - 1 if pagination["page_number"] > 1 else 1
#     for i, music in enumerate(musics_list, start=start):
#         builder.button(
#             text=str(i), callback_data=PaginatedMusicsCallbackFactory(action="paginate", value=str(music.id))
#         )
#     if pagination["page_number"] > 1:
#         builder.button(
#             text="prev", callback_data=PaginatedMusicsCallbackFactory(action="prev", **pagination)
#         )
#     if pagination["page_number"] < pagination["num_pages"]:
#         builder.button(
#             text="next", callback_data=PaginatedMusicsCallbackFactory(action="next", **pagination)
#         )   
        
#     builder.adjust(2)
#     return builder.as_markup()


async def paginated_musics_kb(query, pagination, session):
    response = await session.execute(query)
    musics_list = response.scalars().all()
    nums_bnt_list = []
    for i, music in enumerate(musics_list, start=calculate_start(pagination["page_number"], pagination["page_size"])):
        nums_bnt_list.append(
            types.InlineKeyboardButton(text=str(i), callback_data=PaginatedMusicsCallbackFactory(action="paginate", value=str(music.id)).pack())
        )
    buttons = [
        nums_bnt_list,
    ]
    
    paginate_btn_list = []
    if pagination["page_number"] > 1:
        paginate_btn_list.append(
            types.InlineKeyboardButton(text="◀️ prev", callback_data=PaginatedMusicsCallbackFactory(action="prev", **pagination).pack())
        )
    if pagination["page_number"] < pagination["num_pages"]:
        paginate_btn_list.append(
            types.InlineKeyboardButton(text="▶️ next", callback_data=PaginatedMusicsCallbackFactory(action="next", **pagination).pack())
        )  
    buttons.append(paginate_btn_list)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
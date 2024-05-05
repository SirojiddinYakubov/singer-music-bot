from aiogram import types
from aiogram.utils.i18n import gettext as _
from bot.callbacks import PaginatedMusicsCallbackFactory, PaginatedPurchasesCallbackFactory
from bot.pagination import calculate_start

async def paginated_musics_ikb(query, pagination, session):
    response = await session.execute(query)
    musics_list = response.scalars().all()
    nums_bnt_list = []
    for i, music in enumerate(musics_list, start=calculate_start(pagination["page_number"], pagination["page_size"])):
        nums_bnt_list.append(
            types.InlineKeyboardButton(text=str(i), callback_data=PaginatedMusicsCallbackFactory(action="paginate", value=music.id).pack())
        )
    buttons = [
        nums_bnt_list,
    ]
    
    paginate_btn_list = []
    if pagination["page_number"] > 1:
        paginate_btn_list.append(
            types.InlineKeyboardButton(text=_("◀️ oldingi"), callback_data=PaginatedMusicsCallbackFactory(action="prev", **pagination).pack())
        )
    if pagination["page_number"] < pagination["num_pages"]:
        paginate_btn_list.append(
            types.InlineKeyboardButton(text=_("▶️ keyingi"), callback_data=PaginatedMusicsCallbackFactory(action="next", **pagination).pack())
        )  
    buttons.append(paginate_btn_list)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

async def paginated_purchases_ikb(query, pagination, session):
    buttons = []
    paginate_btn_list = []
    if pagination["page_number"] > 1:
        paginate_btn_list.append(
            types.InlineKeyboardButton(text=_("◀️ oldingi"), callback_data=PaginatedPurchasesCallbackFactory(action="purchase_prev", **pagination).pack())
        )
    if pagination["page_number"] < pagination["num_pages"]:
        paginate_btn_list.append(
            types.InlineKeyboardButton(text=_("▶️ keyingi"), callback_data=PaginatedPurchasesCallbackFactory(action="purchase_next", **pagination).pack())
        )
    buttons.append(paginate_btn_list)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
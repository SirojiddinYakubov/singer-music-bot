from typing import Optional
from aiogram.filters.callback_data import CallbackData

class LangCallbackFactory(CallbackData, prefix="lang_code"):
    action: str
    value: Optional[str] = None
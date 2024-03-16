from typing import Optional
from aiogram.filters.callback_data import CallbackData

class LangCallbackFactory(CallbackData, prefix="lang_code"):
    action: str
    value: Optional[str] = None
    
    
class PaginatedMusicsCallbackFactory(CallbackData, prefix="page"):
    action: str
    page_number: int | None = None
    page_size: int | None = None
    num_pages: int | None = None
    total_results: int | None = None
    value: int | None = None
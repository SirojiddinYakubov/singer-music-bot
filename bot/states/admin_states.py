from aiogram.fsm.state import StatesGroup, State

class SearchMusicState(StatesGroup):
    title = State()
    
class AddMusicState(StatesGroup):
    audio = State()
    price = State()
from aiogram.fsm.state import State, StatesGroup


class GameCreation(StatesGroup):
    waiting_for_theme = State()
    
class GameJoining(StatesGroup):
    waiting_for_code = State()
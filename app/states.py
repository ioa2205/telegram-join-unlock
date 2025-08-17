# app/states.py
from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    add_slug_name = State()
    add_slug_label = State()
    add_slug_file = State()

    broadcast_confirm = State()
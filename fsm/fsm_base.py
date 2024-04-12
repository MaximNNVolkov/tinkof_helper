from aiogram.fsm.state import State, StatesGroup


class StateUser(StatesGroup):
    change_role = State()

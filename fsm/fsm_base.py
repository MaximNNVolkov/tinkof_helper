from aiogram.fsm.state import State, StatesGroup


class StateBonds(StatesGroup):
    enter_ticker = State()

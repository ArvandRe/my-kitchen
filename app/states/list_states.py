from aiogram.fsm.state import State, StatesGroup


class ListStates(StatesGroup):
    waiting_for_ingredient = State()

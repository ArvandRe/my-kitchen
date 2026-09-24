from aiogram.fsm.state import State, StatesGroup


class EditRecipeStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_category = State()
    waiting_for_ingredients = State()
    waiting_for_steps = State()

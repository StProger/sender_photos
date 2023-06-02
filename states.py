from aiogram.dispatcher.filters.state import State, StatesGroup

class NewInterval(StatesGroup):
    new_interval = State()
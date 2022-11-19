from aiogram.dispatcher.filters.state import State, StatesGroup

class Order(StatesGroup):
    message = State()
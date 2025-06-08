from telebot.handler_backends import State, StatesGroup

class DeliveryStates(StatesGroup):
    address = State()
    phone = State()
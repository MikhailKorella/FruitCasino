from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def build_mode_choice():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🎰 Бесплатный режим", callback_data="mode_free"),
        InlineKeyboardButton("💰 Платный режим", callback_data="mode_paid")
    )
    return markup

def build_spin_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("🔄 Крутить снова", callback_data="spin_again"))
    return markup

def build_topup_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("➕ Пополнить баланс", callback_data="topup_balance"))
    return markup

def build_mode_switch_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🔁 Переключиться в бесплатный режим", callback_data="switch_to_free")
    )
    return markup
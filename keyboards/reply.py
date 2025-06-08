from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def main_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🎰 Крутить слоты"),
        KeyboardButton("💰 Баланс"),
        KeyboardButton("➕ Пополнить"),
        KeyboardButton("ℹ️ Факт о фрукте"),
        KeyboardButton("🆘 Помощь"),
        KeyboardButton("📝 Правила"),
    )
    return markup
from telebot.types import Message, ReplyKeyboardRemove
from keyboards.inline import build_mode_choice

def register(bot):
    @bot.message_handler(commands=['start'])
    def start_handler(msg: Message):
        bot.send_message(
            msg.chat.id,
            "Добро пожаловать в Фруктовое Казино!\nВыберите режим игры:",
            reply_markup=build_mode_choice()
        )

    @bot.message_handler(commands=['help'])
    def help_handler(msg: Message):
        help_text = (
            "🍎 Фруктовое Казино - Помощь 🍎\n"
            "/start - начать игру\n"
            "/help - показать это сообщение\n"
            "/rules - правила игры\n"
            "/spin - крутить слоты\n"
            "/fact - случайный факт о фруктах\n"
            "/balance - показать баланс"
        )
        bot.send_message(msg.chat.id, help_text)

    @bot.message_handler(commands=['rules'])
    def mode_handler(msg: Message):
        rules_text = "Правила игры:\n" \
        "За одну крутку вам выпадает три предмета. Чтобы выиграть фрукт, нужно, чтобы на первой позиции выпала тележка, а на второй или третьей - фрукт.\n" \
        "Выпавший фрукт вы выиграли, можете заказать его доставку до дома (если не бесплатный режим)"
        bot.send_message(msg.chat.id, rules_text)
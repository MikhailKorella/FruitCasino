from telebot.types import CallbackQuery, Message, ReplyKeyboardRemove
from keyboards.inline import build_spin_keyboard, build_mode_switch_keyboard, build_topup_keyboard
from keyboards.reply import main_keyboard
from utils.slot_machine import spin_slots
from services.google_sheets import GoogleSheetsService
from services.api_client import get_fruit_fact
from states.delivery_states import DeliveryStates
from utils.logger import logger

# Инициализация сервиса Google Sheets
google_sheets = GoogleSheetsService()

# Временное хранилище пользователей
users = {}

# Доступные фрукты и их эмодзи
FRUITS = {
    "🍌": "Банан",
    "🍑": "Персик", 
    "🍋": "Лимон",
    "🍐": "Грушу",
    "🍏": "Зеленое яблоко",
    "🍍": "Ананас",
    "🥝": "Киви",
    "🥭": "Манго",
    "🍅": "Помидор",
    "🍺": "Пиво"
}

def register(bot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("mode_"))
    def mode_selected(call: CallbackQuery):
        user_id = call.from_user.id
        mode = call.data.split("_")[1]
        
        users[user_id] = {
            "mode": mode,
            "balance": 0 if mode == "paid" else 10,  # В платном режиме начинаем с 0
            "wins": 0,
            "total_spins": 0,
            "pending_delivery": None  # Для хранения выигранного фрукта
        }
        
        bot.edit_message_text(
            f"Режим '{'Платный' if mode == 'paid' else 'Бесплатный'}' активирован!\n"
            f"💰 Баланс: {users[user_id]['balance']} круток",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=None
        )
        bot.send_message(call.message.chat.id, "Выберите действие:", reply_markup=main_keyboard())

    def process_spin(user_id, chat_id, message_id=None):
        user = users.get(user_id)
        if not user:
            if message_id:
                bot.answer_callback_query(user_id, "Сначала выберите режим игры через /start")
            else:
                bot.send_message(chat_id, "Сначала выберите режим игры через /start")
            return

        if user['balance'] <= 0:
            if user['mode'] == "paid":
                markup = build_mode_switch_keyboard()
                if message_id:
                    try:
                        bot.edit_message_text(
                            "💰 В платном режиме баланс пополняется только реальными деньгами.\n"
                            "Хотите переключиться в бесплатный режим с неограниченными крутками?",
                            chat_id,
                            message_id,
                            reply_markup=markup
                        )
                    except Exception as e:
                        logger.error(f"Error editing message: {e}")
                        bot.answer_callback_query(user_id, "Платежная система в разработке", show_alert=True)
                else:
                    bot.send_message(
                        chat_id,
                        "💰 В платном режиме баланс пополняется только реальными деньгами.\n"
                        "Хотите переключиться в бесплатный режим с неограниченными крутками?",
                        reply_markup=markup
                    )
            else:
                if message_id:
                    try:
                        bot.edit_message_text(
                            "❌ Ваш баланс равен 0",
                            chat_id,
                            message_id,
                            reply_markup=build_topup_keyboard()  # Добавляем кнопку пополнения
                        )
                    except Exception as e:
                        logger.error(f"Error editing message: {e}")
                        bot.answer_callback_query(user_id, "Ваш баланс равен 0. Введите /topup", show_alert=True)
                else:
                    bot.send_message(chat_id, "❌ Ваш баланс равен 0. Введите /topup для пополнения")
            return

        # Основная логика вращения
        symbols, win_fruit = spin_slots()
        result = " ".join(symbols)
        user['total_spins'] += 1
        user['balance'] -= 1
        
        if win_fruit:
            user['wins'] += 1
            user['pending_delivery'] = win_fruit
            response = (
                f"{result}\n"
                f"🎉 Поздравляем! Вы выиграли {FRUITS.get(win_fruit, win_fruit)}!\n\n"
                "Чтобы получить приз (в бесплатном режиме приз не приедет), оформите доставку:\n"
                "Введите команду /delivery"
            )
        else:
            response = f"{result}\n😢 Не повезло... Попробуйте еще раз!\n💰 Баланс: {user['balance']}"

        if message_id:
            try:
                bot.edit_message_text(
                    response,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=build_spin_keyboard()
                )
            except Exception as e:
                logger.error(f"Error editing message: {e}")
                bot.answer_callback_query(user_id, "Произошла ошибка, попробуйте еще раз")
        else:
            bot.send_message(chat_id, response, reply_markup=build_spin_keyboard())

    @bot.message_handler(commands=['delivery'])
    def start_delivery(msg: Message):
        user = users.get(msg.from_user.id)
        if not user:
            bot.send_message(msg.chat.id, "Сначала выберите режим игры через /start")
            return
            
        if not user.get('pending_delivery'):
            bot.send_message(msg.chat.id, "❌ У вас нет выигрышей для доставки")
            return
            
        if not google_sheets.connected:
            bot.send_message(msg.chat.id, "⚠️ Сервис доставки временно недоступен")
            return

        bot.send_message(
            msg.chat.id,
            "🚚 Оформление доставки:\n"
            "Введите ваш адрес (город, улица, дом, квартира):"
        )
        bot.set_state(msg.from_user.id, DeliveryStates.address, msg.chat.id)

    @bot.message_handler(state=DeliveryStates.address)
    def process_address(msg: Message):
        bot.add_data(msg.from_user.id, address=msg.text)
        bot.send_message(
            msg.chat.id,
            "📱 Теперь введите ваш номер телефона для связи:"
        )
        bot.set_state(msg.from_user.id, DeliveryStates.phone, msg.chat.id)

    @bot.message_handler(state=DeliveryStates.phone)
    def process_phone(msg: Message):
        user = users.get(msg.from_user.id)
        if not user or not user.get('pending_delivery'):
            bot.send_message(msg.chat.id, "❌ Ошибка: нет данных о выигрыше")
            bot.delete_state(msg.from_user.id, msg.chat.id)
            return
   
        with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
            delivery_data = {
                'id': msg.from_user.id,
                'username': msg.from_user.username,
                'first_name': msg.from_user.first_name,
                'fruit': user['pending_delivery'],
                'address': data.get('address'),
                'phone': msg.text
            }
            
            success = google_sheets.save_delivery_info(delivery_data, user.get("pending_delivery"))
            
            if success:
                response = (
                    "✅ Заказ на доставку оформлен!\n\n"
                    f"🍏 Фрукт: {FRUITS.get(user['pending_delivery'], user['pending_delivery'])}\n"
                    f"🏠 Адрес: {data.get('address')}\n"
                    f"📞 Телефон: {msg.text}\n\n"
                    "Мы свяжемся с вами для подтверждения."
                )
                user['pending_delivery'] = None  # Сбрасываем ожидающую доставку
            else:
                response = "❌ Ошибка при оформлении. Попробуйте позже."
            
            bot.send_message(msg.chat.id, response)
            bot.delete_state(msg.from_user.id, msg.chat.id)

    @bot.message_handler(func=lambda msg: msg.text == "🎰 Крутить слоты" or msg.text == "/spin")
    def spin_handler(msg: Message):
        process_spin(msg.from_user.id, msg.chat.id)

    @bot.callback_query_handler(func=lambda call: call.data == "spin_again")
    def spin_again_handler(call):
        process_spin(call.from_user.id, call.message.chat.id, call.message.message_id)

    @bot.callback_query_handler(func=lambda call: call.data == "switch_to_free")
    def switch_to_free_handler(call: CallbackQuery):
        user_id = call.from_user.id
        users[user_id] = {
            "mode": "free",
            "balance": float('inf'),
            "wins": 0,
            "total_spins": 0,
            "pending_delivery": None
        }
        
        bot.edit_message_text(
            "✅ Вы переключены в бесплатный режим!\n"
            "Теперь у вас неограниченное количество круток!",
            call.message.chat.id,
            call.message.message_id
        )
        bot.send_message(call.message.chat.id, "Выберите действие:", reply_markup=main_keyboard())

    @bot.message_handler(func=lambda msg: msg.text == "💰 Баланс" or msg.text == "/balance")
    def balance_handler(msg: Message):
        user = users.get(msg.from_user.id)
        if not user:
            bot.send_message(msg.chat.id, "Сначала выберите режим игры через /start")
            return
            
        balance_text = (
            f"📊 Ваш баланс:\n"
            f"• Режим: {'Платный' if user['mode'] == 'paid' else 'Бесплатный'}\n"
            f"• Круток: {'∞' if user['balance'] == float('inf') else user['balance']}\n"
            f"• Выигрышей: {user['wins']}\n"
            f"• Всего круток: {user['total_spins']}"
        )
        
        if user.get('pending_delivery'):
            balance_text += f"\n\n🍏 Ожидает доставки: {FRUITS.get(user['pending_delivery'], user['pending_delivery'])}"
        
        bot.send_message(msg.chat.id, balance_text)

    @bot.message_handler(func=lambda msg: msg.text == "ℹ️ Факт о фрукте" or msg.text == "/fact")
    def fact_handler(msg: Message):
        fact = get_fruit_fact()
        bot.send_message(msg.chat.id, fact)
    
    @bot.message_handler(func=lambda msg: msg.text == "➕ Пополнить" or msg.text == "/topup")
    def topup_handler(msg: Message):
        user = users.get(msg.from_user.id)
        if not user:
            bot.send_message(msg.chat.id, "Сначала выберите режим игры через /start")
            return
            
        if user['mode'] == "paid":
            markup = build_mode_switch_keyboard()
            bot.send_message(
                msg.chat.id,
                "💰 В платном режиме пополнение временно недоступно.\n"
                "Хотите переключиться в бесплатный режим?",
                reply_markup=markup
            )
            return
            
        bot.send_message(msg.chat.id, "Введите количество круток для пополнения:")
        bot.register_next_step_handler(msg, process_topup_amount)

    @bot.message_handler(func=lambda msg: msg.text == "🆘 Помощь" or msg.text == "/help")
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
    
    @bot.message_handler(func=lambda msg: msg.text == "📝 Правила" or msg.text == "/rules")
    def rules_handler(msg: Message):
        rules_text = "Правила игры:\n" \
        "За одну крутку вам выпадает три предмета. Чтобы выиграть фрукт, нужно, чтобы на первой позиции выпала тележка, а на второй или третьей - фрукт.\n" \
        "Выпавший фрукт вы выиграли, можете заказать его доставку до дома (если не бесплатный режим)"
        bot.send_message(msg.chat.id, rules_text)

    @bot.callback_query_handler(func=lambda call: call.data == "topup_balance")
    def topup_callback_handler(call: CallbackQuery):
        user = users.get(call.from_user.id)
        if not user:
            bot.answer_callback_query(call.id, "Сначала выберите режим игры через /start")
            return
        
        if user['mode'] == "paid":
            bot.answer_callback_query(call.id, "В платном режиме пополнение временно недоступно", show_alert=True)
            return
        
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "Введите количество круток для пополнения:"
        )
        bot.register_next_step_handler(call.message, process_topup_amount)

    def process_topup_amount(msg: Message):
        try:
            amount = int(msg.text)
            if amount <= 0:
                bot.send_message(msg.chat.id, "❌ Введите положительное число!")
                return
                
            user = users.get(msg.from_user.id)
            if not user:
                bot.send_message(msg.chat.id, "❌ Ошибка пользователя")
                return
                
            user['balance'] += amount
            bot.send_message(
                msg.chat.id,
                f"✅ Баланс пополнен на {amount} круток!\n"
                f"💰 Текущий баланс: {user['balance']}",
                reply_markup=build_spin_keyboard()  # Добавляем кнопку "Крутить снова"
            )
        except ValueError:
            bot.send_message(msg.chat.id, "❌ Пожалуйста, введите число!", reply_markup=main_keyboard())
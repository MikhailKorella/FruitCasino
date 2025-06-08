from telebot.types import Message
from states.delivery_states import DeliveryStates
from services.google_sheets import GoogleSheetsService
from utils.logger import logger

google_sheets = GoogleSheetsService()

def register_delivery_handlers(bot):
    @bot.message_handler(commands=['delivery'])
    def start_delivery(msg: Message):
        if not google_sheets.connected:
            bot.send_message(msg.chat.id, "⚠️ Сервис доставки временно недоступен")
            return

        bot.send_message(
            msg.chat.id,
            "🚚 Для оформления доставки выигранного фрукта нам нужны некоторые данные.\n"
            "Пожалуйста, введите ваш полный адрес доставки (город, улица, дом, квартира):"
        )
        bot.set_state(msg.from_user.id, DeliveryStates.address, msg.chat.id)

    @bot.message_handler(state=DeliveryStates.address)
    def process_address(msg: Message):
        bot.add_data(msg.from_user.id, address=msg.text)
        bot.send_message(
            msg.chat.id,
            "📱 Теперь введите ваш номер телефона для связи в формате +79991234567:"
        )
        bot.set_state(msg.from_user.id, DeliveryStates.phone, msg.chat.id)

    @bot.message_handler(state=DeliveryStates.phone)
    def process_phone(msg: Message):
        with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
            user_data = {
                'id': msg.from_user.id,
                'username': msg.from_user.username,
                'first_name': msg.from_user.first_name,
                'address': data.get('address'),
                'phone': msg.text,
                'fruit': data.get('fruit', 'Фруктовая корзина')
            }
            
            success = google_sheets.save_delivery_info(user_data, user_data['fruit'])
            
            if success:
                response = (
                    "✅ Заказ на доставку успешно оформлен!\n\n"
                    f"🍏 Выигранный фрукт: {user_data['fruit']}\n"
                    f"🏠 Адрес доставки: {user_data['address']}\n"
                    f"📞 Контактный телефон: {user_data['phone']}\n\n"
                    "Мы свяжемся с вами в течение 24 часов для подтверждения заказа."
                )
            else:
                response = (
                    "❌ Произошла ошибка при оформлении заказа.\n"
                    "Попробуйте позже или свяжитесь с поддержкой @support."
                )
            
            bot.send_message(msg.chat.id, response)
            bot.delete_state(msg.from_user.id, msg.chat.id)
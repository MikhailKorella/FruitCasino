from telebot import TeleBot
from telebot.custom_filters import StateFilter
from telebot.storage import StateMemoryStorage
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config.settings import BOT_TOKEN
from utils.logger import logger, setup_logger
import routers.commands as commands
import routers.handlers as specific
import routers.delivery_handlers as delivery

logger = setup_logger()
state_storage = StateMemoryStorage()
bot = TeleBot(BOT_TOKEN, state_storage=state_storage)

bot.add_custom_filter(StateFilter(bot))
commands.register(bot)
specific.register(bot)
delivery.register_delivery_handlers(bot)

if __name__ == '__main__':
    logger.info("Bot started")
    bot.infinity_polling()
import logging

def setup_logger():
    logger = logging.getLogger("bot")
    logger.setLevel(logging.INFO)
    
    # Логирование в файл
    file_handler = logging.FileHandler("bot.log")
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    
    # Логирование в консоль
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

# Инициализируем глобальный логгер
logger = setup_logger()
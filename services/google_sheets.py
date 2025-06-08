import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging
from datetime import datetime
from config.settings import GOOGLE_SHEET_ID, GOOGLE_CREDENTIALS_PATH
import os

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    def __init__(self):
        self.sheet = None
        self.connected = False  # Добавляем атрибут connected
        self.connect()

    def connect(self):
        """Установка соединения с Google Sheets"""
        try:
            if not os.path.exists(GOOGLE_CREDENTIALS_PATH):
                logger.error(f"Credentials file not found at {GOOGLE_CREDENTIALS_PATH}")
                self.connected = False
                return False

            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                GOOGLE_CREDENTIALS_PATH, scope
            )
            client = gspread.authorize(creds)
            self.sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
            self.connected = True  # Устанавливаем флаг подключения
            logger.info("Successfully connected to Google Sheets")
            return True
        except Exception as e:
            logger.error(f"Error connecting to Google Sheets: {e}")
            self.sheet = None
            self.connected = False
            return False

    def save_delivery_info(self, user_data: dict, fruit: str) -> bool:
        """Сохраняет информацию о доставке в Google Sheets"""
        if not self.connected or not self.sheet:
            if not self.connect():  # Пытаемся переподключиться
                return False

        try:
            row = [
                str(user_data.get('id', '')),
                user_data.get('username', ''),
                user_data.get('first_name', ''),
                fruit,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                user_data.get('address', ''),
                user_data.get('phone', ''),
                'Новый заказ'
            ]
            self.sheet.append_row(row)
            logger.info(f"Successfully saved delivery info for {user_data.get('id')}")
            return True
        except Exception as e:
            logger.error(f"Error saving to Google Sheets: {e}")
            self.connected = False  # Сбрасываем флаг при ошибке
            return False

    def get_delivery_status(self, user_id: str):
        """Проверяет статус доставки"""
        if not self.connected or not self.sheet:
            if not self.connect():
                return None

        try:
            records = self.sheet.get_all_records()
            for record in records:
                if str(record['ID']) == str(user_id):
                    return {
                        'fruit': record['Фрукт'],
                        'date': record['Дата'],
                        'status': record['Статус заказа']
                    }
            return None
        except Exception as e:
            logger.error(f"Error reading from Google Sheets: {e}")
            self.connected = False
            return None
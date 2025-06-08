from dotenv import load_dotenv
import os
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")
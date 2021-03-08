from dotenv import load_dotenv

load_dotenv()

import os

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
INTRA_CLIENT_ID = os.getenv('INTRA_CLIENT_ID')
INTRA_CLIENT_SECRET = os.getenv('INTRA_CLIENT_SECRET')
INTRA_REDIRECT_URI = os.getenv('INTRA_REDIRECT_URI')

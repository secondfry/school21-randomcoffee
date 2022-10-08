from dotenv import load_dotenv

load_dotenv()

import os

ENV = os.getenv("ENV", "production")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")
OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI")
OAUTH_ENDPOINT_TOKEN = os.getenv(
    "OAUTH_ENDPOINT_TOKEN", "https://oauth.secondfry.ru/api/oauth/token"
)
OAUTH_ENDPOINT_AUTHORIZE = os.getenv(
    "OAUTH_ENDPOINT_AUTHORIZE", "https://oauth.secondfry.ru/api/oauth/authorize"
)
OAUTH_ENDPOINT_AUTHENTICATE = os.getenv(
    "OAUTH_ENDPOINT_AUTHENTICATE", "https://oauth.secondfry.ru/api/oauth/authenticate"
)

ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS").split(",")]
SAVIOUR_ID = int(os.getenv("SAVIOUR_ID"))

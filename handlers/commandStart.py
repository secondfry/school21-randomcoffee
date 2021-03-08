import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, PicklePersistence

from config.env import INTRA_CLIENT_ID, INTRA_REDIRECT_URI

TOKEN_REGEXP = re.compile('[0-9a-f]{64}')


def get_oauth_endpoint() -> str:
    return 'https://api.intra.42.fr/oauth/authorize?client_id={}&redirect_uri={}&response_type=code'.format(
        INTRA_CLIENT_ID,
        INTRA_REDIRECT_URI
    )


def check_if_token(context: CallbackContext) -> bool:
    if not len(context.args):
        return False

    token = context.args[0]
    match = TOKEN_REGEXP.match(token)
    if match is None:
        return False

    return True


def do_auth(update: Update, context: CallbackContext, persistence: PicklePersistence) -> None:
    pass


def do_greet(update: Update, context: CallbackContext) -> None:
    greeting = "Привет!\n\nЭто бот неофициального RandomCoffee Школы 21.\n\nДля начала давай познакомимся поближе – " \
               "пройди аутентификацию через Intra OAuth."

    kbd = [
        [
            InlineKeyboardButton(
                "Аутентификация",
                url=get_oauth_endpoint()
            ),
        ]
    ]

    context.bot.send_message(chat_id=update.effective_chat.id, text=greeting, reply_markup=InlineKeyboardMarkup(kbd))


def handler_command_start(update: Update, context: CallbackContext, persistence: PicklePersistence) -> None:
    if check_if_token(context):
        return do_auth(update, context, persistence)

    return do_greet(update, context)

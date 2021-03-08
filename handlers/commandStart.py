import re
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, PicklePersistence

from config.env import INTRA_CLIENT_ID, INTRA_REDIRECT_URI
from utils.oauthClient import check_access_code, get_token_user, TokenUser, Campus

TOKEN_REGEXP = re.compile('[0-9a-f]{64}')
USER_DATA_TOKEN_SUCCESS = 'intra_token_success'
USER_DATA_LOGIN = 'intra_login'
USER_DATA_CAMPUS = 'intra_campus'


def get_oauth_endpoint() -> str:
    return 'https://api.intra.42.fr/oauth/authorize?client_id={}&redirect_uri={}&response_type=code'.format(
        INTRA_CLIENT_ID,
        INTRA_REDIRECT_URI
    )


def check_if_token(context: CallbackContext) -> bool:
    if not len(context.args):
        return False

    access_code = context.args[0]
    match = TOKEN_REGEXP.match(access_code)
    if match is None:
        return False

    return True


def get_primary_campus(data: TokenUser) -> Optional[Campus]:
    if not data['campus']:
        return None

    id: Optional[int] = None

    for campus_user in data['campus_users']:
        if campus_user['is_primary']:
            id = campus_user['campus_id']

    if not id:
        return None

    for campus in data['campus']:
        if campus['id'] == id:
            return campus

    return None


def do_auth(update: Update, context: CallbackContext, persistence: PicklePersistence) -> None:
    access_code = context.args[0]

    token_success = check_access_code(access_code)
    if not token_success:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Твой код – не код (либо интра лежит, тогда попробуй позднее).'
        )
        return

    token_user = get_token_user(token_success['access_token'])
    if not token_user:
        # FIXME JobQueue
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Интра лежит, попробуй позднее.'
        )
        return

    context.user_data[USER_DATA_TOKEN_SUCCESS] = token_success
    context.user_data[USER_DATA_LOGIN] = token_user['login']
    context.user_data[USER_DATA_CAMPUS] = get_primary_campus(token_user)

    try:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='privet {} iz {}'.format(token_user['login'], get_primary_campus(token_user)['name'])
        )
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text='privet {}'.format(token_user['login']))


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

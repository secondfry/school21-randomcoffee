from typing import Optional, List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from config.constants import TOKEN_REGEXP, USER_DATA_TOKEN_SUCCESS, USER_DATA_TELEGRAM_USERNAME, USER_DATA_LOGIN
from config.env import INTRA_CLIENT_ID, INTRA_REDIRECT_URI
from utils.oauthClient import check_access_code, TokenUser, Campus, TokenSuccess, GetTokenRequest


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


def enqueue_get_token_user(queue_data: List[GetTokenRequest], id: int, token_success: TokenSuccess):
    queue_data.append({
        'id': id,
        'token': token_success
    })


def do_auth(update: Update, context: CallbackContext, queue_data: List[GetTokenRequest]) -> None:
    access_code = context.args[0]

    token_success = check_access_code(access_code)
    if not token_success:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Твой код – не код (либо интра лежит, тогда попробуй позднее).'
        )
        return

    context.user_data[USER_DATA_TOKEN_SUCCESS] = token_success
    enqueue_get_token_user(queue_data, update.effective_user.id, token_success)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Ожидаю ответ Интры...'
    )


def do_greet(update: Update, context: CallbackContext) -> None:
    greeting = "Привет!\n\nЭто бот неофициального случайного кофе Школы 21.\n\nДля начала давай познакомимся поближе " \
               "– пройди аутентификацию через Intra OAuth. "

    kbd = [
        [
            InlineKeyboardButton(
                "Аутентификация",
                url=get_oauth_endpoint()
            ),
        ]
    ]

    context.user_data[USER_DATA_TELEGRAM_USERNAME] = update.effective_chat.username
    context.bot.send_message(chat_id=update.effective_chat.id, text=greeting, reply_markup=InlineKeyboardMarkup(kbd))


def handler_command_start(update: Update, context: CallbackContext, queue_data: List[GetTokenRequest]) -> None:
    if context.user_data.get(USER_DATA_LOGIN):
        return

    if check_if_token(context):
        return do_auth(update, context, queue_data)

    return do_greet(update, context)

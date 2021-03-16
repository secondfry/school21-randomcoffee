from typing import List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from config.constants import (
    TOKEN_REGEXP,
    USER_DATA_V1_TELEGRAM_USERNAME,
    USER_DATA_V1_AUTHORIZED,
    USER_DATA_V1_INTRA_TOKEN,
)
from config.env import INTRA_CLIENT_ID, INTRA_REDIRECT_URI
from typings import GetTokenRequest, Token
from utils.lang import COMMAND_START_NOT_AUTHORIZED, COMMAND_DENIED_AUTHORIZED
from utils.oauthClient import check_access_code


def get_oauth_endpoint() -> str:
    return 'https://api.intra.42.fr/oauth/authorize?client_id={}&redirect_uri={}&response_type=code'.format(
        INTRA_CLIENT_ID,
        INTRA_REDIRECT_URI
    )


def do_reject(upd: Update, ctx: CallbackContext) -> None:
    ctx.bot.send_message(upd.effective_user.id, text=COMMAND_DENIED_AUTHORIZED)


def check_if_token(context: CallbackContext) -> bool:
    if not len(context.args):
        return False

    access_code = context.args[0]
    match = TOKEN_REGEXP.match(access_code)
    if match is None:
        return False

    return True


def enqueue_get_token_user(queue_data: List[GetTokenRequest], id: int, token_success: Token):
    queue_data.append({
        'id': id,
        'token': token_success
    })


def do_auth(upd: Update, ctx: CallbackContext, queue_data: List[GetTokenRequest]) -> None:
    code = ctx.args[0]

    token = check_access_code(code)
    if not token:
        ctx.bot.send_message(
            chat_id=upd.effective_chat.id,
            text='Твой код – не код (либо интра лежит, тогда попробуй позднее).'
        )
        return

    ctx.user_data[USER_DATA_V1_INTRA_TOKEN] = token
    enqueue_get_token_user(queue_data, upd.effective_user.id, token)
    ctx.bot.send_message(
        chat_id=upd.effective_chat.id,
        text='Ожидаю ответ Интры...'
    )


def do_greet(upd: Update, ctx: CallbackContext) -> None:
    kbd = [
        [
            InlineKeyboardButton(
                "Аутентификация",
                url=get_oauth_endpoint()
            ),
        ]
    ]

    ctx.user_data[USER_DATA_V1_AUTHORIZED] = False
    username = upd.effective_chat.username
    ctx.user_data[USER_DATA_V1_TELEGRAM_USERNAME] = username if username else '???'
    ctx.bot.send_message(
        chat_id=upd.effective_chat.id,
        text=COMMAND_START_NOT_AUTHORIZED,
        reply_markup=InlineKeyboardMarkup(kbd)
    )


def handler_command_start(upd: Update, ctx: CallbackContext, queue_data: List[GetTokenRequest]) -> None:
    if ctx.user_data.get(USER_DATA_V1_AUTHORIZED, False):
        return do_reject(upd, ctx)

    if check_if_token(ctx):
        return do_auth(upd, ctx, queue_data)

    return do_greet(upd, ctx)

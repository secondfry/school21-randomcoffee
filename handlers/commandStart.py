from typing import Optional, Tuple, Union

import telegram
from config.constants import (
    AUTH_DATA_REGEXP,
    KEY_AUTHORIZED,
    KEY_OAUTH_STATE,
    KEY_OAUTH_TOKEN,
    KEY_TELEGRAM_USERNAME,
    KEY_USER_ID,
)
from config.env import (
    ENV,
    OAUTH_CLIENT_ID,
    OAUTH_CLIENT_SECRET,
    OAUTH_ENDPOINT_AUTHENTICATE,
    OAUTH_ENDPOINT_AUTHORIZE,
    OAUTH_ENDPOINT_TOKEN,
    OAUTH_REDIRECT_URI,
)
from oauthlib import common as oauthlib_common
from requests_oauthlib import OAuth2Session
from telegram import ext as telegram_ext
from typings import Token, TokenUser
from utils.lang import COMMAND_DENIED_AUTHORIZED, COMMAND_START_NOT_AUTHORIZED

from handlers.commandSettings import settings_choose_campus

oauth = OAuth2Session(OAUTH_CLIENT_ID, redirect_uri=OAUTH_REDIRECT_URI)


async def do_reject(upd: telegram.Update) -> None:
    await upd.message.reply_text(COMMAND_DENIED_AUTHORIZED)


def check_if_auth_data(
    ctx: telegram_ext.CallbackContext,
) -> Tuple[bool, Union[None, str]]:
    if not ctx.args:
        return False, None

    auth_data = ctx.args[0]
    match = AUTH_DATA_REGEXP.match(auth_data)
    if not match:
        # TODO(secondfry): report to user that his input is wrong.
        return False, None

    code = auth_data[:40]
    state = auth_data[40:]
    if ENV == "production" and state != ctx.user_data[KEY_OAUTH_STATE]:
        return False, None

    return True, code


def check_access_code(code: str) -> Optional[Token]:
    token = oauth.fetch_token(
        OAUTH_ENDPOINT_TOKEN,
        code=code,
        client_secret=OAUTH_CLIENT_SECRET,
    )
    return token


def get_token_user() -> Optional[TokenUser]:
    res = oauth.post(OAUTH_ENDPOINT_AUTHENTICATE)

    if res.status_code == 200:
        data: TokenUser = res.json()
        return data

    return None


async def do_auth(
    upd: telegram.Update,
    ctx: telegram_ext.CallbackContext,
    code: str,
) -> None:
    token = check_access_code(code)
    if not token:
        await ctx.bot.send_message(
            chat_id=upd.effective_chat.id,
            text="Твой код авторизации – не код авторизации (либо OAuth Provider лежит, тогда попробуй позднее).",
        )
        return

    ctx.user_data[KEY_OAUTH_TOKEN] = token
    token_user = get_token_user()
    if not token_user:
        await ctx.bot.send_message(
            chat_id=upd.effective_chat.id,
            text="Либо OAuth Provider лежит, либо там какой-то багос. Напиши автору бота!",
        )
        return

    ctx.user_data[KEY_AUTHORIZED] = True
    ctx.user_data[KEY_USER_ID] = token_user["user_id"]

    try:
        await upd.message.reply_text("Привет, {}".format(token_user["login"]))
    except:
        # TODO actually handle exception
        pass

    await settings_choose_campus(ctx, upd.effective_user.id)


async def do_greet(upd: telegram.Update, ctx: telegram_ext.CallbackContext) -> None:
    state = oauthlib_common.generate_token(length=24)
    ctx.user_data[KEY_OAUTH_STATE] = state
    authorization_url, state = oauth.authorization_url(
        OAUTH_ENDPOINT_AUTHORIZE, state=state
    )

    kbd = [
        [
            telegram.InlineKeyboardButton("Авторизация", url=authorization_url),
        ]
    ]

    ctx.user_data[KEY_AUTHORIZED] = False
    username = upd.effective_chat.username
    ctx.user_data[KEY_TELEGRAM_USERNAME] = username if username else "???"
    await upd.message.reply_text(
        COMMAND_START_NOT_AUTHORIZED, reply_markup=telegram.InlineKeyboardMarkup(kbd)
    )


async def handler_command_start(
    upd: telegram.Update, ctx: telegram_ext.CallbackContext
) -> None:
    if ctx.user_data.get(KEY_AUTHORIZED, False):
        return await do_reject(upd)

    status, code = check_if_auth_data(ctx)
    if status:
        return await do_auth(upd, ctx, code)

    # TODO(secondfry): remove all inline buttons in chat
    return await do_greet(upd, ctx)

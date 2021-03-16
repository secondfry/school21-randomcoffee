from typing import Dict, Any

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from config.constants import (
    USER_DATA_V1_SETTINGS_CAMPUS,
    USER_DATA_V1_SETTINGS_ONLINE,
    USER_DATA_V1_INTRA_LOGIN,
    USER_DATA_V1_INTRA_CAMPUS,
    USER_DATA_V1_SETTINGS_ACTIVE,
    USER_DATA_V1_AUTHORIZED,
    USER_DATA_V1_TELEGRAM_USERNAME,
    USER_DATA_V1_MATCH_WITH,
)
from config.env import ADMIN_IDS
from utils.lang import COMMAND_DENIED_NOT_AUTHORIZED


def info(data: Dict[str, Any], is_admin_request: bool = False) -> str:
    fields = [
        USER_DATA_V1_INTRA_LOGIN,
        USER_DATA_V1_INTRA_CAMPUS,
        USER_DATA_V1_SETTINGS_CAMPUS,
        USER_DATA_V1_SETTINGS_ONLINE,
        USER_DATA_V1_SETTINGS_ACTIVE,
        USER_DATA_V1_TELEGRAM_USERNAME,
    ]

    if is_admin_request:
        fields.append(USER_DATA_V1_MATCH_WITH)

    return '\n'.join(['{}: {}'.format(x, data.get(x, '???')) for x in fields])


def info_other(upd: Update, ctx: CallbackContext) -> None:
    param = ctx.args[0]
    user = None

    for uid, udata in ctx.dispatcher.user_data.items():
        if USER_DATA_V1_INTRA_LOGIN not in udata:
            continue

        if udata[USER_DATA_V1_INTRA_LOGIN] == param:
            user = udata
            break

        if str(uid) == param:
            user = udata
            break

    if not user:
        ctx.bot.send_message(upd.effective_user.id, text='{} not found'.format(param))
        return

    message = info(user, is_admin_request=True)
    ctx.bot.send_message(
        upd.effective_user.id,
        text='```\ntelegram.id: {}\n{}\n```'.format(
            uid,
            message
        ),
        parse_mode=ParseMode.MARKDOWN
    )


def info_self(upd: Update, ctx: CallbackContext) -> None:
    message = info(ctx.user_data)
    ctx.bot.send_message(upd.effective_user.id, text='```\n{}\n```'.format(message), parse_mode=ParseMode.MARKDOWN)


def handler_command_info(upd: Update, ctx: CallbackContext) -> None:
    if not ctx.user_data.get(USER_DATA_V1_AUTHORIZED, False):
        ctx.bot.send_message(upd.effective_user.id, text=COMMAND_DENIED_NOT_AUTHORIZED)
        return

    if ctx.args and upd.effective_user.id in ADMIN_IDS:
        return info_other(upd, ctx)

    return info_self(upd, ctx)

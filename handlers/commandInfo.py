from typing import Any, Dict

import telegram
from config.constants import (
    KEY_AUTHORIZED,
    KEY_OAUTH_STATE,
    KEY_OAUTH_TOKEN,
    KEY_SETTINGS_ACTIVE,
    KEY_SETTINGS_CAMPUS,
    KEY_SETTINGS_ONLINE,
    KEY_TELEGRAM_ID,
    KEY_TELEGRAM_USERNAME,
    KEY_USER_CAMPUS,
    KEY_USER_ID,
)
from config.env import ADMIN_IDS
from telegram import constants as telegram_constants
from telegram import ext as telegram_ext
from utils.lang import COMMAND_DENIED_NOT_AUTHORIZED


def info(data: Dict[str, Any], is_admin_request: bool = False) -> str:
    if is_admin_request:
        fields = [x for x in list(data.keys()) if x not in [KEY_OAUTH_STATE, KEY_OAUTH_TOKEN]]
        fields.sort()
    else:
        fields = [
            KEY_SETTINGS_ACTIVE,
            KEY_SETTINGS_CAMPUS,
            KEY_SETTINGS_ONLINE,
            KEY_TELEGRAM_USERNAME,
            KEY_USER_ID,
        ]

    return "\n".join(["{}: {}".format(x, data.get(x, "???")) for x in fields])


async def info_other(upd: telegram.Update, ctx: telegram_ext.CallbackContext) -> None:
    param = ctx.args[0]
    user = None

    for uid, udata in ctx.application.user_data.items():
        if KEY_USER_ID not in udata:
            continue

        if udata[KEY_USER_ID] == param:
            user = udata
            break

        if str(uid) == param:
            user = udata
            break

    if not user:
        await upd.message.reply_text("{} not found".format(param))
        return

    message = info(user, is_admin_request=True)
    await upd.message.reply_text(
        "```\n{}```".format(message),
        parse_mode=telegram_constants.ParseMode.MARKDOWN,
    )


async def info_self(upd: telegram.Update, ctx: telegram_ext.CallbackContext) -> None:
    message = info(ctx.user_data)
    await upd.message.reply_text(
        "```\n{}\n```".format(message),
        parse_mode=telegram_constants.ParseMode.MARKDOWN,
    )


async def handler_command_info(
    upd: telegram.Update, ctx: telegram_ext.CallbackContext
) -> None:
    if not ctx.user_data.get(KEY_AUTHORIZED, False):
        await upd.message.reply_text(COMMAND_DENIED_NOT_AUTHORIZED)
        return

    if ctx.args and upd.effective_user.id in ADMIN_IDS:
        return await info_other(upd, ctx)

    return await info_self(upd, ctx)

import logging
from typing import Optional, Union

import telegram
from config.constants import KEY_AUTHORIZED, KEY_TELEGRAM_USERNAME, KEY_USER_ID
from config.env import ADMIN_IDS
from telegram import constants as telegram_constants
from telegram import error as telegram_error
from telegram import ext as telegram_ext


async def handle_common_block_errors(
    ctx: telegram_ext.CallbackContext, uid: int, ex: telegram_error.TelegramError
):
    if str(ex) not in [
        "Forbidden: bot was blocked by the user",
        "Forbidden: user is deactivated",
    ]:
        return False

    udata = ctx.application.user_data[uid]

    try:
        await ctx.bot.send_message(
            ADMIN_IDS[0],
            text="`[t#{0:<10}] {2:<8}` @{1} <= removed due to exception {3}".format(
                uid,
                udata.get(KEY_TELEGRAM_USERNAME, "???").replace("_", "\\_"),
                udata[KEY_USER_ID],
                str(ex),
            ),
            parse_mode=telegram_constants.ParseMode.MARKDOWN,
        )
    except Exception as e:
        logging.error("Could not send error report!\n%s", e)

    udata.clear()
    udata[KEY_AUTHORIZED] = False
    return True


async def send_error(
    ctx: telegram_ext.CallbackContext,
    uid: Union[int, None],
    message: Optional[str],
    ex: Exception,
):
    udata = ctx.application.user_data.get(uid, {})
    telegram_username = udata.get(KEY_TELEGRAM_USERNAME, "???")
    intra_login = udata.get(KEY_USER_ID, "???")

    if not message:
        message = "Unspecified error."

    try:
        await ctx.bot.send_message(
            ADMIN_IDS[0],
            text="Exception with [tid#{}][tus#{}] {}.\n{}\n{}".format(
                uid,
                telegram_username,
                intra_login,
                message,
                ex,
            ),
        )
    except Exception as e:
        logging.error("Could not send error report!\n%s", e)


async def handler_error(
    upd: Optional[telegram.Update], ctx: telegram_ext.CallbackContext
):
    await send_error(
        ctx,
        upd.effective_user.id if upd and upd.effective_user else None,
        "Root update: {}".format(upd),
        ctx.error,
    )
    logging.error('telegram.Update "%s" caused error "%s"', upd, ctx.error)

import logging

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
    udata.clear()
    udata[KEY_AUTHORIZED] = False
    return True


async def send_error(
    ctx: telegram_ext.CallbackContext,
    uid: int,
    telegram_username: str,
    intra_login: str,
    message: str,
    ex: Exception,
):
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


async def handler_error(upd: telegram.Update, ctx: telegram_ext.CallbackContext):
    await send_error(
        ctx,
        upd.effective_user.id,
        ctx.user_data.get(KEY_TELEGRAM_USERNAME, "???"),
        ctx.user_data.get(KEY_USER_ID, "???"),
        "Root update: {}".format(upd),
        ctx.error,
    )
    logging.warning('telegram.Update "%s" caused error "%s"', upd, ctx.error)

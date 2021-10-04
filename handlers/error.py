import logging

from config.constants import (USER_DATA_V1_AUTHORIZED,
                              USER_DATA_V1_INTRA_LOGIN,
                              USER_DATA_V1_TELEGRAM_USERNAME)
from config.env import ADMIN_IDS
from telegram import Update
from telegram.error import TelegramError
from telegram.ext import CallbackContext
from telegram.parsemode import ParseMode


def handle_common_block_errors(ctx: CallbackContext, uid: int, ex: TelegramError):
    if str(ex) not in [
        'Forbidden: bot was blocked by the user',
        'Forbidden: user is deactivated',
    ]:
        return False

    udata = ctx.dispatcher.user_data[uid]

    ctx.bot.send_message(ADMIN_IDS[0], text='`[t#{0:<10}] {2:<8}` @{1} <= removed due to exception {}'.format(
        uid,
        udata.get(USER_DATA_V1_TELEGRAM_USERNAME, '???').replace('_', '\\_'),
        udata[USER_DATA_V1_INTRA_LOGIN],
        str(ex)
    ), parse_mode=ParseMode.MARKDOWN)
    udata.clear()
    udata[USER_DATA_V1_AUTHORIZED] = False
    return True


def send_error(ctx: CallbackContext, uid: int, telegram_username: str, intra_login: str, message: str, ex: Exception):
    ctx.bot.send_message(
        ADMIN_IDS[0],
        text='Exception with [tid#{}][tus#{}] {}.\n{}\n{}'.format(
            uid,
            telegram_username,
            intra_login,
            message,
            ex,
        )
    )


def handler_error(upd: Update, ctx: CallbackContext):
    send_error(
        ctx,
        upd.effective_user.id,
        ctx.user_data.get(USER_DATA_V1_TELEGRAM_USERNAME, '???'),
        ctx.user_data.get(USER_DATA_V1_INTRA_LOGIN, '???'),
        'Root update: {}'.format(upd),
        ctx.error
    )
    logging.warning('Update "%s" caused error "%s"', upd, ctx.error)

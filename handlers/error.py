import logging

from telegram import Update
from telegram.ext import CallbackContext

from config.constants import USER_DATA_V1_TELEGRAM_USERNAME, USER_DATA_V1_INTRA_LOGIN
from config.env import ADMIN_IDS


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

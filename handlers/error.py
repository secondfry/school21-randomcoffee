import logging

from telegram import Update
from telegram.ext import CallbackContext

from config.env import ADMIN_IDS


def handler_error(upd: Update, ctx: CallbackContext):
    ctx.bot.send_message(ADMIN_IDS[0], text='Update {} caused error {}'.format(upd, ctx.error))
    logging.warning('Update "%s" caused error "%s"', upd, ctx.error)

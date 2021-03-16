from telegram import Update
from telegram.ext import CallbackContext

from config.constants import USER_DATA_V1_AUTHORIZED
from utils.lang import COMMAND_DENIED_NOT_AUTHORIZED


def handler_command_stop(upd: Update, ctx: CallbackContext) -> None:
    if not ctx.user_data.get(USER_DATA_V1_AUTHORIZED, False):
        ctx.bot.send_message(upd.effective_user.id, text=COMMAND_DENIED_NOT_AUTHORIZED)
        return

    ctx.user_data.clear()
    ctx.bot.send_message(upd.effective_user.id, text='До новых встреч!')

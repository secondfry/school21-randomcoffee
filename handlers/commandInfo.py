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
)
from utils.lang import COMMAND_DENIED_NOT_AUTHORIZED


def handler_command_info(upd: Update, ctx: CallbackContext) -> None:
    if not ctx.user_data.get(USER_DATA_V1_AUTHORIZED, False):
        ctx.bot.send_message(upd.effective_user.id, text=COMMAND_DENIED_NOT_AUTHORIZED)
        return

    message = '\n'.join(['{}: {}'.format(x, ctx.user_data.get(x, '???')) for x in [
        USER_DATA_V1_INTRA_LOGIN,
        USER_DATA_V1_INTRA_CAMPUS,
        USER_DATA_V1_SETTINGS_CAMPUS,
        USER_DATA_V1_SETTINGS_ONLINE,
        USER_DATA_V1_SETTINGS_ACTIVE,
        USER_DATA_V1_TELEGRAM_USERNAME
    ]])
    ctx.bot.send_message(upd.effective_user.id, text='```\n{}\n```'.format(message), parse_mode=ParseMode.MARKDOWN)

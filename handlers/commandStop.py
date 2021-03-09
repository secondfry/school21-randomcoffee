from telegram import Update
from telegram.ext import CallbackContext

from config.constants import USER_DATA_LOGIN


def handler_command_stop(update: Update, context: CallbackContext) -> None:
    if not context.user_data.get(USER_DATA_LOGIN):
        return

    context.user_data.clear()
    context.bot.send_message(update.effective_user.id, text='До новых встреч!')

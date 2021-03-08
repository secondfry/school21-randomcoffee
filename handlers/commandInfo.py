from telegram import Update
from telegram.ext import CallbackContext

from config.constants import USER_DATA_LOGIN


def handler_command_info(update: Update, context: CallbackContext) -> None:
    data = 'login: {}'.format(context.user_data.get(USER_DATA_LOGIN))
    context.bot.send_message(update.effective_user.id, text=data)

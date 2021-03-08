from telegram import Update
from telegram.ext import CallbackContext

from config.constants import USER_DATA_LOGIN, USER_DATA_CAMPUS, USER_DATA_ONLINE, USER_DATA_TELEGRAM_USERNAME


def handler_command_info(update: Update, context: CallbackContext) -> None:
    data = 'intra: {}\ntelegram: @{}\ncampus: {}\nonline: {}'.format(
        context.user_data.get(USER_DATA_LOGIN),
        context.user_data.get(USER_DATA_TELEGRAM_USERNAME),
        context.user_data.get(USER_DATA_CAMPUS),
        context.user_data.get(USER_DATA_ONLINE),
    )
    context.bot.send_message(update.effective_user.id, text=data)

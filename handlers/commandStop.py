from telegram import Update
from telegram.ext import CallbackContext


def handler_command_stop(update: Update, context: CallbackContext) -> None:
    context.user_data.clear()
    context.bot.send_message(update.effective_user.id, text='До новых встреч!')

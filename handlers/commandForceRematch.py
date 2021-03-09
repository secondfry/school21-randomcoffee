from telegram import Update
from telegram.ext import CallbackContext

from config.env import ADMIN_IDS
from utils.performRematch import perform_rematch


def handler_command_forcerematch(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return

    context.bot.send_message(update.effective_user.id, text='monkaS')
    perform_rematch(context)

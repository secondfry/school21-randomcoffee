from telegram import Update
from telegram.ext import CallbackContext

from config.env import ADMIN_IDS
from utils.performMatch import perform_match


def handler_command_forcematch(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return

    context.bot.send_message(update.effective_user.id, text='monkaS')
    perform_match(context)

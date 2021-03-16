from telegram import Update
from telegram.ext import CallbackContext

from config.env import ADMIN_IDS
from utils.performRematch import perform_rematch


def handler_command_forcerematch(upd: Update, ctx: CallbackContext) -> None:
    if upd.effective_user.id not in ADMIN_IDS:
        return

    ctx.bot.send_message(upd.effective_user.id, text='monkaS')
    perform_rematch(ctx)

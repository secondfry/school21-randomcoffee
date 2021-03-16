from telegram import Update
from telegram.ext import CallbackContext

from config.env import ADMIN_IDS
from handlers.commandDump import handler_command_dump
from utils.performMatch import perform_match


def handler_command_forcematch(upd: Update, ctx: CallbackContext) -> None:
    if upd.effective_user.id not in ADMIN_IDS:
        return

    perform_match(ctx)
    handler_command_dump(upd, ctx)

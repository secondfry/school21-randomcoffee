import telegram
from config.env import ADMIN_IDS
from telegram import ext as telegram_ext
from utils.performMatch import perform_match


async def handler_command_forcematch(
    upd: telegram.Update, ctx: telegram_ext.CallbackContext
) -> None:
    if upd.effective_user.id not in ADMIN_IDS:
        return

    await perform_match(ctx)

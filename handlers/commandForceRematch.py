import telegram
from config.env import ADMIN_IDS
from telegram import ext as telegram_ext
from utils.performRematch import perform_rematch


async def handler_command_forcerematch(
    upd: telegram.Update, ctx: telegram_ext.CallbackContext
) -> None:
    if upd.effective_user.id not in ADMIN_IDS:
        return

    await perform_rematch(ctx)

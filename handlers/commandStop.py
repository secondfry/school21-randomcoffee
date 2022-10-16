import telegram
from config.constants import KEY_AUTHORIZED
from telegram import ext as telegram_ext
from utils.lang import COMMAND_DENIED_NOT_AUTHORIZED


async def handler_command_stop(
    upd: telegram.Update, ctx: telegram_ext.CallbackContext
) -> None:
    if not ctx.user_data.get(KEY_AUTHORIZED, False):
        await upd.message.reply_text(COMMAND_DENIED_NOT_AUTHORIZED)
        return

    ctx.user_data.clear()
    await upd.message.reply_text("До новых встреч!")

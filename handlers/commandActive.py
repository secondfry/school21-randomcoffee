import telegram
from config.constants import CALLBACK_ACTIVE_YES, KEY_AUTHORIZED, KEY_SETTINGS_ACTIVE
from telegram import ext as telegram_ext
from utils.lang import COMMAND_DENIED_NOT_AUTHORIZED


async def handler_command_active(
    upd: telegram.Update, ctx: telegram_ext.CallbackContext
) -> None:
    if not ctx.user_data.get(KEY_AUTHORIZED, False):
        await upd.message.reply_text(COMMAND_DENIED_NOT_AUTHORIZED)
        return

    ctx.user_data[KEY_SETTINGS_ACTIVE] = CALLBACK_ACTIVE_YES
    await upd.message.reply_text(
        "Твой статус изменен на активный! Во вторник подберу тебе пару на случайный кофе."
    )

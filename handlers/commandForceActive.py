import telegram
from config.constants import (
    CALLBACK_ACTIVE_NO,
    CALLBACK_ACTIVE_YES,
    KEY_AUTHORIZED,
    KEY_SETTINGS_ACTIVE,
    KEY_TELEGRAM_USERNAME,
    KEY_USER_ID,
)
from config.env import ADMIN_IDS
from telegram import constants as telegram_constants
from telegram import error as telegram_error
from telegram import ext as telegram_ext
from utils.getters import get_accepted_sign

from handlers.commandDump import chunks, perform_dump
from handlers.error import handle_common_block_errors, send_error


async def handler_command_forceactive(
    upd: telegram.Update, ctx: telegram_ext.CallbackContext
):
    if upd.effective_user.id not in ADMIN_IDS:
        return

    activated = []

    for uid, udata in ctx.application.user_data.items():
        # Not authorized – skip
        if not udata.get(KEY_AUTHORIZED, False):
            udata[KEY_AUTHORIZED] = False
            continue

        # Active – skip
        if udata.get(KEY_SETTINGS_ACTIVE, CALLBACK_ACTIVE_NO) == CALLBACK_ACTIVE_YES:
            continue

        udata[KEY_SETTINGS_ACTIVE] = CALLBACK_ACTIVE_YES
        activated.append(
            "[{2}] {1:<8} [t#{0:<10}]".format(
                uid,
                udata[KEY_USER_ID],
                get_accepted_sign(udata),
            )
        )

        try:
            await ctx.bot.send_message(
                uid,
                text="Привет!\n\n"
                "В качестве эксперимента на этой неделе все пользователи становятся активными! "
                "Ато вдруг ты хотел сходить на кофе, но опять забыл или еще чего ;).\n\n"
                "P.S. Ты можешь обратно стать неактивным при помощи настроек /settings",
            )
        except telegram_error.TelegramError as ex:
            if not await handle_common_block_errors(ctx, uid, ex):
                await send_error(
                    ctx,
                    uid,
                    udata[KEY_TELEGRAM_USERNAME],
                    udata[KEY_USER_ID],
                    "Can't send force active message.",
                    ex,
                )
        except Exception as ex:
            await send_error(
                ctx,
                uid,
                udata[KEY_TELEGRAM_USERNAME],
                udata[KEY_USER_ID],
                "Can't send force active message.",
                ex,
            )

    activated.sort()
    await ctx.bot.send_message(ADMIN_IDS[0], text="Активированы")
    for chunk in chunks(activated, 30):
        await ctx.bot.send_message(
            ADMIN_IDS[0],
            text="```\n{}\n```".format("\n".join(chunk)),
            parse_mode=telegram_constants.ParseMode.MARKDOWN,
        )

    await perform_dump(ctx, ADMIN_IDS[0])

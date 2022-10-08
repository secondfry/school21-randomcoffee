import telegram
from config.constants import (
    CALLBACK_ACTIVE_NO,
    CALLBACK_ACTIVE_YES,
    KEY_AUTHORIZED,
    KEY_MATCH_ACCEPTED,
    KEY_MATCH_WITH,
    KEY_SETTINGS_ACTIVE,
    KEY_TELEGRAM_USERNAME,
    KEY_USER_ID,
)
from config.env import ADMIN_IDS
from telegram import constants as telegram_constants
from telegram import error as telegram_error
from telegram import ext as telegram_ext
from utils.getters import get_accepted_sign
from utils.performMatch import send_match_message

from handlers.commandDump import chunks
from handlers.error import handle_common_block_errors, send_error


async def handler_command_forcenotify(
    upd: telegram.Update, ctx: telegram_ext.CallbackContext
):
    if upd.effective_user.id not in ADMIN_IDS:
        return

    notified = []

    for uid, udata in ctx.application.user_data.items():
        # Not authorized – skip
        if not udata.get(KEY_AUTHORIZED, False):
            udata[KEY_AUTHORIZED] = False
            continue

        # Not active – skip
        if udata.get(KEY_SETTINGS_ACTIVE, CALLBACK_ACTIVE_NO) != CALLBACK_ACTIVE_YES:
            udata[KEY_SETTINGS_ACTIVE] = CALLBACK_ACTIVE_NO
            continue

        # Have already accepted match – skip
        if udata.get(KEY_MATCH_ACCEPTED, False):
            continue

        # Has no match to accept – skip
        bid = udata.get(KEY_MATCH_WITH, None)
        if not bid:
            continue

        # Match is not authorized – set accepted to true
        bdata = ctx.application.user_data.get(bid, {})
        if not bdata.get(KEY_AUTHORIZED, False):
            bdata[KEY_AUTHORIZED] = False
            udata[KEY_MATCH_ACCEPTED] = True
            continue

        # Match is not active – set accepted to true
        if bdata.get(KEY_SETTINGS_ACTIVE, CALLBACK_ACTIVE_NO) != CALLBACK_ACTIVE_YES:
            bdata[KEY_SETTINGS_ACTIVE] = CALLBACK_ACTIVE_NO
            udata[KEY_MATCH_ACCEPTED] = True
            continue

        notified.append(
            "[{2}] {1:<8} [t#{0:<10}]".format(
                uid,
                udata[KEY_USER_ID],
                get_accepted_sign(udata),
            )
        )
        try:
            await ctx.bot.send_message(
                uid,
                text="Ой-ой-ой, я запутался кому отправлял уведомления, а кому нет. Не серчай!\n"
                "P.S. Если получение матча не подтвердить, "
                "то бот автоматически сделает тебя неактивным.",
            )
        except telegram_error.TelegramError as ex:
            if not handle_common_block_errors(ctx, uid, ex):
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
        await send_match_message(
            ctx,
            uid,
            bdata.get(KEY_USER_ID, "???"),
            bdata.get(KEY_TELEGRAM_USERNAME, "???"),
        )

    notified.sort()
    await ctx.bot.send_message(ADMIN_IDS[0], text="Уведомлены")
    for chunk in chunks(notified, 30):
        await ctx.bot.send_message(
            ADMIN_IDS[0],
            text="```\n{}\n```".format("\n".join(chunk)),
            parse_mode=telegram_constants.ParseMode.MARKDOWN,
        )

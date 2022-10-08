from config.constants import (
    CALLBACK_ACTIVE_NO,
    CALLBACK_ACTIVE_YES,
    KEY_AUTHORIZED,
    KEY_MATCH_ACCEPTED,
    KEY_MATCH_NOTIFIED,
    KEY_MATCH_WITH,
    KEY_SETTINGS_ACTIVE,
    KEY_TELEGRAM_USERNAME,
    KEY_USER_ID,
)
from config.env import ADMIN_IDS
from handlers.commandDump import perform_dump
from handlers.error import handle_common_block_errors, send_error
from telegram import constants as telegram_constants
from telegram import error as telegram_error
from telegram import ext as telegram_ext

from utils.performMatch import match_algo


async def prepare_users_for_rematch(ctx: telegram_ext.CallbackContext):
    for uid, udata in ctx.application.user_data.items():
        if not udata.get(KEY_AUTHORIZED, False):
            udata[KEY_AUTHORIZED] = False
            continue

        if udata.get(KEY_SETTINGS_ACTIVE, CALLBACK_ACTIVE_NO) != CALLBACK_ACTIVE_YES:
            udata[KEY_SETTINGS_ACTIVE] = CALLBACK_ACTIVE_NO
            continue

        bid = udata.get(KEY_MATCH_WITH, None)
        if bid and not udata.get(KEY_MATCH_ACCEPTED, False):
            bdata = ctx.application.user_data.get(bid, {})
            if bdata is not None and bdata.get(KEY_MATCH_ACCEPTED, False):
                bdata[KEY_MATCH_ACCEPTED] = False
                bdata[KEY_MATCH_NOTIFIED] = False
                bdata[KEY_MATCH_WITH] = None
                try:
                    await ctx.bot.send_message(
                        bid,
                        text="К сожалению, твой пир на случайный кофе не подтвердил встречу...\n"
                        "Ищем нового!",
                    )
                except telegram_error.TelegramError as ex:
                    if not handle_common_block_errors(ctx, bid, ex):
                        await send_error(
                            ctx,
                            bid,
                            bdata[KEY_TELEGRAM_USERNAME],
                            bdata[KEY_USER_ID],
                            "Can't send apology.",
                            ex,
                        )
                except Exception as ex:
                    await send_error(
                        ctx,
                        bid,
                        bdata[KEY_TELEGRAM_USERNAME],
                        bdata[KEY_USER_ID],
                        "Can't send apology.",
                        ex,
                    )
                await ctx.bot.send_message(
                    ADMIN_IDS[0],
                    text="`[t#{0:<10}] {2:<8}` @{1} <= apology".format(
                        bid,
                        bdata.get(KEY_TELEGRAM_USERNAME, "???").replace("_", "\\_"),
                        bdata[KEY_USER_ID],
                    ),
                    parse_mode=telegram_constants.ParseMode.MARKDOWN,
                )

            udata[KEY_SETTINGS_ACTIVE] = CALLBACK_ACTIVE_NO
            udata[KEY_MATCH_ACCEPTED] = False
            udata[KEY_MATCH_NOTIFIED] = False
            udata[KEY_MATCH_WITH] = None
            try:
                await ctx.bot.send_message(
                    uid,
                    text="К сожалению, ты не подтвердил встречу... "
                    "Автоматически выставляю тебе статус inactive.\n"
                    "Ждем тебя, когда вновь появится время на случайный кофе!",
                )
            except telegram_error.TelegramError as ex:
                if not handle_common_block_errors(ctx, uid, ex):
                    await send_error(
                        ctx,
                        uid,
                        udata[KEY_TELEGRAM_USERNAME],
                        udata[KEY_USER_ID],
                        "Can't send inactivity notification.",
                        ex,
                    )
            except Exception as ex:
                await send_error(
                    ctx,
                    uid,
                    udata[KEY_TELEGRAM_USERNAME],
                    udata[KEY_USER_ID],
                    "Can't send inactivity notification.",
                    ex,
                )
            await ctx.bot.send_message(
                ADMIN_IDS[0],
                text="`[t#{0:<10}] {2:<8}` @{1} <= inactive".format(
                    uid,
                    udata.get(KEY_TELEGRAM_USERNAME, "???").replace("_", "\\_"),
                    udata[KEY_USER_ID],
                ),
                parse_mode=telegram_constants.ParseMode.MARKDOWN,
            )


async def perform_rematch(ctx: telegram_ext.CallbackContext) -> None:
    await perform_dump(ctx, ADMIN_IDS[0])
    await prepare_users_for_rematch(ctx)
    await match_algo(ctx)
    await perform_dump(ctx, ADMIN_IDS[0])

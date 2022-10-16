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
from telegram import constants as telegram_constants
from telegram import ext as telegram_ext

from utils.performMatch import match_algo, safe_message


async def prepare_users_for_rematch(ctx: telegram_ext.CallbackContext):
    for uid, udata in ctx.application.user_data.items():
        # NOTE(secondfry): skip users who either never authorized
        # or stopped the bot.
        if not udata.get(KEY_AUTHORIZED, False):
            udata[KEY_AUTHORIZED] = False
            continue

        # NOTE(secondfry): skip inactive users.
        if udata.get(KEY_SETTINGS_ACTIVE, CALLBACK_ACTIVE_NO) != CALLBACK_ACTIVE_YES:
            udata[KEY_SETTINGS_ACTIVE] = CALLBACK_ACTIVE_NO
            continue

        # NOTE(secondfry): skip users who either not matched yet
        # or already accepted.
        bid = udata.get(KEY_MATCH_WITH, None)
        if not bid or udata.get(KEY_MATCH_ACCEPTED, False):
            continue

        # NOTE(secondfry): here we have uid/udata who did not accept the match.
        # Also we have bid of the match.

        bdata = ctx.application.user_data.get(bid, {})
        if bdata is not None and bdata.get(KEY_MATCH_ACCEPTED, False):
            # NOTE(secondfry): bid/bdata has accepted the match.
            # Apology is required.
            bdata[KEY_MATCH_ACCEPTED] = False
            bdata[KEY_MATCH_NOTIFIED] = False
            bdata[KEY_MATCH_WITH] = None
            await safe_message(
                ctx,
                bid,
                err="Can't send apology.",
                text="К сожалению, твой пир на случайный кофе не подтвердил встречу...\n"
                "Ищем нового!",
            )
            await safe_message(
                ctx,
                ADMIN_IDS[0],
                err="Can't send apology notice to admin.",
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
        await safe_message(
            ctx,
            uid,
            err="Can't send inactivity notification.",
            text="К сожалению, ты не подтвердил встречу... "
            "Автоматически выставляю тебе статус inactive.\n"
            "/active вернет тебя в список активных пиров, ждем тебя, когда вновь появится время на случайный кофе!",
        )
        await safe_message(
            ctx,
            ADMIN_IDS[0],
            err="Can't send inactivity notification to admin.",
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

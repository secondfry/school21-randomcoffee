import random
import secrets
from collections import deque
from typing import Callable, Deque, Dict, Optional

import telegram
from config.constants import (
    CALLBACK_ACTIVE_NO,
    CALLBACK_ACTIVE_YES,
    CALLBACK_CAMPUS_KAZAN,
    CALLBACK_CAMPUS_MOSCOW,
    CALLBACK_CAMPUS_NOVOSIBIRSK,
    CALLBACK_CHOOSE_MATCH,
    KEY_AUTHORIZED,
    KEY_MATCH_ACCEPTED,
    KEY_MATCH_NOTIFIED,
    KEY_MATCH_WITH,
    KEY_SETTINGS_ACTIVE,
    KEY_SETTINGS_CAMPUS,
    KEY_TELEGRAM_USERNAME,
    KEY_USER_ID,
)
from config.env import ADMIN_IDS, SAVIOUR_ID
from handlers.commandDump import perform_dump
from handlers.error import handle_common_block_errors, send_error
from telegram import error as telegram_error
from telegram import ext as telegram_ext

from utils.getters import get_bucket
from utils.lang import TEXT_INACTIVE


async def safe_message(
    ctx: telegram_ext.CallbackContext,
    uid: int,
    err: Optional[str] = None,
    cb: Callable = None,
    *args,
    **kwargs,
):
    try:
        await ctx.bot.send_message(uid, *args, **kwargs)
        if cb:
            cb()
    except telegram_error.TelegramError as ex:
        if not handle_common_block_errors(ctx, uid, ex):
            await send_error(ctx, uid, err, ex)
    except Exception as ex:
        await send_error(ctx, uid, err, ex)


async def prepare_users_for_match(ctx: telegram_ext.CallbackContext):
    msg_queue = []

    for uid, udata in ctx.application.user_data.items():
        udata[KEY_MATCH_ACCEPTED] = False
        udata[KEY_MATCH_NOTIFIED] = False
        udata[KEY_MATCH_WITH] = None

        if not udata.get(KEY_AUTHORIZED, False):
            udata[KEY_AUTHORIZED] = False
            continue

        if udata.get(KEY_SETTINGS_ACTIVE, CALLBACK_ACTIVE_NO) != CALLBACK_ACTIVE_YES:
            udata[KEY_SETTINGS_ACTIVE] = CALLBACK_ACTIVE_NO
            msg_queue.append(uid)
            continue

    for uid in msg_queue:
        await safe_message(
            ctx, uid, text=TEXT_INACTIVE, err="Can't send inactivity notice."
        )


async def send_match_message(
    ctx: telegram_ext.CallbackContext, fromid: int, tologin: str, tohandle: str
) -> None:
    kbd = [
        [
            telegram.InlineKeyboardButton(
                "Подтвердить встречу", callback_data=CALLBACK_CHOOSE_MATCH
            )
        ]
    ]

    def cb():
        ctx.application.user_data[fromid][KEY_MATCH_NOTIFIED] = True

    await safe_message(
        ctx,
        fromid,
        err="Can't send match message.",
        cb=cb,
        text="Твой случайный кофе на этой неделе...\nC пиром {} [tg: @{}]!\n\nПодтверди получение сообщения:".format(
            tologin, tohandle
        ),
        reply_markup=telegram.InlineKeyboardMarkup(kbd),
    )


async def match(ctx: telegram_ext.CallbackContext, aid: int, bid: int) -> None:
    adata = ctx.application.user_data[aid]
    adata[KEY_MATCH_WITH] = bid
    alogin = adata[KEY_USER_ID]
    atelegram = adata[KEY_TELEGRAM_USERNAME]

    bdata = ctx.application.user_data[bid]
    bdata[KEY_MATCH_WITH] = aid
    blogin = bdata[KEY_USER_ID]
    atelegram = bdata[KEY_TELEGRAM_USERNAME]

    await send_match_message(ctx, aid, blogin, atelegram)
    await send_match_message(ctx, bid, alogin, atelegram)


def find_peer_from_campus(
    uids: Deque[int], user_campuses: Dict[int, str], campus: str
) -> Optional[int]:
    for uid in uids:
        if user_campuses[uid] == campus:
            uids.remove(uid)
            return uid
    if uids:
        return uids.pop()
    return None


async def no_coffee(ctx: telegram_ext.CallbackContext, uid: int):
    await safe_message(
        ctx,
        uid,
        err="Can't send apology to peer left without pair.",
        text="Волей судьбы ты остался сегодня без пары на случайный кофе.",
    )


async def match_algo(ctx: telegram_ext.CallbackContext):
    buckets: Dict[str, Deque[int]] = {
        CALLBACK_CAMPUS_KAZAN: deque(),
        CALLBACK_CAMPUS_MOSCOW: deque(),
        CALLBACK_CAMPUS_NOVOSIBIRSK: deque(),
        "online": deque(),
        "???": deque(),
    }
    user_campuses = {}

    for uid, udata in ctx.application.user_data.items():
        if not udata.get(KEY_AUTHORIZED, False):
            udata[KEY_AUTHORIZED] = False
            continue

        if udata.get(KEY_SETTINGS_ACTIVE, CALLBACK_ACTIVE_NO) != CALLBACK_ACTIVE_YES:
            udata[KEY_SETTINGS_ACTIVE] = CALLBACK_ACTIVE_NO
            continue

        if udata.get(KEY_MATCH_WITH, None):
            continue

        udata[KEY_MATCH_ACCEPTED] = False
        udata[KEY_MATCH_NOTIFIED] = False

        bucket = get_bucket(udata)

        campus = udata.get(KEY_SETTINGS_CAMPUS, "???")
        user_campuses[uid] = campus

        buckets[bucket].append(uid)

    for bucket, uids in buckets.items():
        random.shuffle(uids, random=lambda: secrets.randbelow(100) / 100.0)

    for bucket, uids in buckets.items():
        if bucket == "???":
            if uids:
                await safe_message(
                    ctx,
                    ADMIN_IDS[0],
                    text=f"For some reason ??? bucket has #{len(uids)} accounts in it",
                )
            continue

        while len(uids) > 1:
            aid = uids.pop()
            bid = uids.pop()

            async def job(ctx: telegram_ext.CallbackContext):
                await match(ctx, aid, bid)

            ctx.application.job_queue.run_once(job, when=0)

        if not uids:
            continue

        if bucket != "online":
            aid = uids.pop()
            bid = find_peer_from_campus(
                buckets["online"], user_campuses, user_campuses[aid]
            )

            if not bid:
                await no_coffee(ctx, aid)
                continue

            async def job(ctx: telegram_ext.CallbackContext):
                await match(ctx, aid, bid)

            ctx.application.job_queue.run_once(job, when=0)

        if bucket == "online":
            aid = uids.pop()

            if True:
                await no_coffee(ctx, aid)
            else:
                # TODO reimplement saviour mechanic
                bid = SAVIOUR_ID

                async def job(ctx: telegram_ext.CallbackContext):
                    await match(ctx, aid, bid)

                ctx.application.job_queue.run_once(job, when=0)

    buckets.clear()
    user_campuses.clear()


async def perform_match(ctx: telegram_ext.CallbackContext) -> None:
    await perform_dump(ctx, ADMIN_IDS[0])
    await prepare_users_for_match(ctx)
    await match_algo(ctx)
    await perform_dump(ctx, ADMIN_IDS[0])

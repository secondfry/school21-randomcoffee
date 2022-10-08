import random
import secrets
from collections import deque
from typing import Deque, Dict, Optional

import telegram
from config.constants import (
    CALLBACK_ACTIVE_NO,
    CALLBACK_ACTIVE_YES,
    CALLBACK_CAMPUS_KAZAN,
    CALLBACK_CAMPUS_MOSCOW,
    CALLBACK_CAMPUS_NOVOSIBIRSK,
    KEY_AUTHORIZED,
    KEY_MATCH_ACCEPTED,
    KEY_MATCH_NOTIFIED,
    KEY_MATCH_WITH,
    KEY_SETTINGS_ACTIVE,
    KEY_SETTINGS_CAMPUS,
    KEY_TELEGRAM_USERNAME,
    KEY_USER_ID,
)
from config.env import ADMIN_IDS
from handlers.commandDump import perform_dump
from handlers.error import handle_common_block_errors, send_error
from telegram import error as telegram_error
from telegram import ext as telegram_ext

from utils.getters import get_bucket


async def prepare_users_for_match(ctx: telegram_ext.CallbackContext):
    for uid, udata in ctx.application.user_data.items():
        udata[KEY_MATCH_ACCEPTED] = False
        udata[KEY_MATCH_NOTIFIED] = False
        udata[KEY_MATCH_WITH] = None

        if not udata.get(KEY_AUTHORIZED, False):
            udata[KEY_AUTHORIZED] = False
            continue

        if udata.get(KEY_SETTINGS_ACTIVE, CALLBACK_ACTIVE_NO) != CALLBACK_ACTIVE_YES:
            udata[KEY_SETTINGS_ACTIVE] = CALLBACK_ACTIVE_NO
            try:
                await ctx.bot.send_message(
                    uid,
                    text="На этой неделе ты выбрал не идти на случайный кофе.\n"
                    "Если передумаешь и изменишь настройки, "
                    "то завтра тебе должно будет подобрать пару.",
                )
            except telegram_error.TelegramError as ex:
                if not handle_common_block_errors(ctx, uid, ex):
                    await send_error(
                        ctx,
                        uid,
                        udata[KEY_TELEGRAM_USERNAME],
                        udata[KEY_USER_ID],
                        "Can't send inactivity notice.",
                        ex,
                    )
            except Exception as ex:
                await send_error(
                    ctx,
                    uid,
                    udata[KEY_TELEGRAM_USERNAME],
                    udata[KEY_USER_ID],
                    "Can't send inactivity notice.",
                    ex,
                )
            continue


async def send_match_message(
    ctx: telegram_ext.CallbackContext, fromid: int, tologin: str, tohandle: str
) -> None:
    kbd = [
        [
            telegram.InlineKeyboardButton(
                "Подтвердить встречу", callback_data="match-accept"
            )
        ]
    ]

    try:
        await ctx.bot.send_message(
            fromid,
            text="Твой случайный кофе на этой неделе...\nC пиром {} [tg: @{}]!\n\nПодтверди получение сообщения:".format(
                tologin, tohandle
            ),
            reply_markup=telegram.InlineKeyboardMarkup(kbd),
        )
        ctx.application.user_data[fromid][KEY_MATCH_NOTIFIED] = True
    except:
        # TODO actually handle exception
        pass


async def match(
    ctx: telegram_ext.CallbackContext,
    aid: int,
    bid: int,
    alogin: str,
    blogin: str,
    ahandle: str,
    bhandle: str,
) -> None:
    ctx.application.user_data[aid][KEY_MATCH_WITH] = bid
    ctx.application.user_data[bid][KEY_MATCH_WITH] = aid
    await send_match_message(ctx, aid, blogin, bhandle)
    await send_match_message(ctx, bid, alogin, ahandle)


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


async def match_algo(ctx: telegram_ext.CallbackContext):
    buckets: Dict[str, Deque[int]] = {
        CALLBACK_CAMPUS_KAZAN: deque(),
        CALLBACK_CAMPUS_MOSCOW: deque(),
        CALLBACK_CAMPUS_NOVOSIBIRSK: deque(),
        "online": deque(),
        "???": deque(),
    }
    user_campuses = {}
    user_handles = {}
    user_logins = {}

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

        handle = udata.get(KEY_TELEGRAM_USERNAME, "???")
        user_handles[uid] = handle

        login = udata.get(KEY_USER_ID, "???")
        user_logins[uid] = login

        campus = udata.get(KEY_SETTINGS_CAMPUS, "???")
        user_campuses[uid] = campus

        buckets[bucket].append(uid)

    for bucket, uids in buckets.items():
        random.shuffle(uids, random=lambda: secrets.randbelow(100) / 100.0)

    for bucket, uids in buckets.items():
        if bucket == "???":
            if uids:
                await ctx.bot.send_message(
                    ADMIN_IDS[0],
                    text="For some reason ??? bucket has #{} accounts in it".format(
                        len(uids)
                    ),
                )
            continue

        while len(uids) > 1:
            a = uids.pop()
            b = uids.pop()
            await match(
                ctx,
                a,
                b,
                user_logins.get(a),
                user_logins.get(b),
                user_handles.get(a),
                user_handles.get(b),
            )

        if not uids:
            continue

        if bucket != "online":
            a = uids.pop()
            b = find_peer_from_campus(
                buckets["online"], user_campuses, user_campuses[a]
            )

            if not b:
                continue

            await match(
                ctx,
                a,
                b,
                user_logins.get(a),
                user_logins.get(b),
                user_handles.get(a),
                user_handles.get(b),
            )

        # TODO reimplement saviour mechanic
        # if bucket == 'online':
        #     a = uids.pop()
        #     b = SAVIOUR_ID
        #     match(ctx, a, b, logins.get(a), logins.get(b), handles.get(a), handles.get(b))

    buckets.clear()
    user_campuses.clear()
    user_handles.clear()
    user_logins.clear()


async def perform_match(ctx: telegram_ext.CallbackContext) -> None:
    await perform_dump(ctx, ADMIN_IDS[0])
    await prepare_users_for_match(ctx)
    await match_algo(ctx)
    await perform_dump(ctx, ADMIN_IDS[0])

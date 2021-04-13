import random
import secrets
from collections import deque
from typing import Dict, Deque, Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, TelegramError, ParseMode
from telegram.ext import CallbackContext

from config.constants import (
    CALLBACK_CAMPUS_KAZAN,
    CALLBACK_CAMPUS_MOSCOW,
    USER_DATA_V1_TELEGRAM_USERNAME,
    USER_DATA_V1_INTRA_LOGIN,
    USER_DATA_V1_MATCH_ACCEPTED,
    USER_DATA_V1_MATCH_WITH,
    USER_DATA_V1_SETTINGS_ACTIVE,
    CALLBACK_ACTIVE_NO,
    USER_DATA_V1_AUTHORIZED,
    CALLBACK_ACTIVE_YES,
    USER_DATA_V1_SETTINGS_CAMPUS,
    USER_DATA_V1_MATCH_NOTIFIED,
)
from config.env import ADMIN_IDS
from handlers.error import send_error
from utils.getters import get_bucket


def send_match_message(ctx: CallbackContext, fromid: int, tologin: str, tohandle: str) -> None:
    kbd = [
        [
            InlineKeyboardButton('Подтвердить встречу', callback_data='match-accept')
        ]
    ]

    try:
        ctx.bot.send_message(
            fromid,
            text='Твой случайный кофе на этой неделе...\nC пиром {} [tg: @{}]!\n\nПодтверди получение сообщения:'.format(
                tologin,
                tohandle
            ),
            reply_markup=InlineKeyboardMarkup(kbd)
        )
        ctx.dispatcher.user_data[fromid][USER_DATA_V1_MATCH_NOTIFIED] = True
    except:
        # TODO actually handle exception
        pass


def match(ctx: CallbackContext, aid: int, bid: int, alogin: str, blogin: str, ahandle: str, bhandle: str) -> None:
    ctx.dispatcher.user_data[aid][USER_DATA_V1_MATCH_WITH] = bid
    ctx.dispatcher.user_data[bid][USER_DATA_V1_MATCH_WITH] = aid
    send_match_message(ctx, aid, blogin, bhandle)
    send_match_message(ctx, bid, alogin, ahandle)


def find_peer_from_campus(
        uids: Deque[int],
        user_campuses: Dict[int, str],
        campus: str
) -> Optional[int]:
    for uid in uids:
        if user_campuses[uid] == campus:
            return uid
    return None


def perform_match(ctx: CallbackContext) -> None:
    buckets: Dict[str, Deque[int]] = {
        CALLBACK_CAMPUS_KAZAN: deque(),
        CALLBACK_CAMPUS_MOSCOW: deque(),
        'online': deque(),
        '???': deque(),
    }
    user_campuses = {}
    user_handles = {}
    user_logins = {}

    for uid, udata in ctx.dispatcher.user_data.items():
        udata[USER_DATA_V1_MATCH_ACCEPTED] = False
        udata[USER_DATA_V1_MATCH_NOTIFIED] = False
        udata[USER_DATA_V1_MATCH_WITH] = None

        if not udata.get(USER_DATA_V1_AUTHORIZED, False):
            udata[USER_DATA_V1_AUTHORIZED] = False
            continue

        if udata.get(USER_DATA_V1_SETTINGS_ACTIVE, CALLBACK_ACTIVE_NO) != CALLBACK_ACTIVE_YES:
            udata[USER_DATA_V1_SETTINGS_ACTIVE] = CALLBACK_ACTIVE_NO
            try:
                ctx.bot.send_message(uid, text='На этой неделе ты выбрал не идти на случайный кофе.\n'
                                               'Если передумаешь и изменишь настройки, '
                                               'то завтра тебе должно будет подобрать пару.')
            except TelegramError as ex:
                if str(ex) == 'Forbidden: bot was blocked by the user':
                    ctx.bot.send_message(ADMIN_IDS[0], text='`[t#{0:<10}] {2:<8}` @{1} <= removed due to being blocked'.format(
                        uid,
                        udata.get(USER_DATA_V1_TELEGRAM_USERNAME, '???').replace('_', '\\_'),
                        udata[USER_DATA_V1_INTRA_LOGIN]
                    ), parse_mode=ParseMode.MARKDOWN)
                    udata.clear()
                    udata[USER_DATA_V1_AUTHORIZED] = False
                else:
                    send_error(ctx, uid, udata[USER_DATA_V1_TELEGRAM_USERNAME], udata[USER_DATA_V1_INTRA_LOGIN],
                               'Can\'t send inactivity notice.', ex)
            except Exception as ex:
                send_error(ctx, uid, udata[USER_DATA_V1_TELEGRAM_USERNAME], udata[USER_DATA_V1_INTRA_LOGIN],
                           'Can\'t send inactivity notice.', ex)
            continue

        bucket = get_bucket(udata)

        handle = udata.get(USER_DATA_V1_TELEGRAM_USERNAME, '???')
        user_handles[uid] = handle

        login = udata.get(USER_DATA_V1_INTRA_LOGIN, '???')
        user_logins[uid] = login

        campus = udata.get(USER_DATA_V1_SETTINGS_CAMPUS, '???')
        user_campuses[uid] = campus

        buckets[bucket].append(uid)

    for bucket, uids in buckets.items():
        random.shuffle(uids, random=lambda: secrets.randbelow(100) / 100.0)

    for bucket, uids in buckets.items():
        if bucket == '???':
            if uids:
                ctx.bot.send_message(
                    ADMIN_IDS[0],
                    text='For some reason ??? bucket has #{} accounts in it'.format(len(uids))
                )
            continue

        while len(uids) > 1:
            a = uids.pop()
            b = uids.pop()
            match(ctx, a, b, user_logins.get(a), user_logins.get(b), user_handles.get(a), user_handles.get(b))

        if not uids:
            continue

        if bucket != 'online':
            a = uids.pop()
            b = find_peer_from_campus(buckets['online'], user_campuses, user_campuses[a])

            if not b:
                continue

            match(ctx, a, b, user_logins.get(a), user_logins.get(b), user_handles.get(a), user_handles.get(b))

        # TODO reimplement saviour mechanic
        # if bucket == 'online':
        #     a = uids.pop()
        #     b = SAVIOUR_ID
        #     match(ctx, a, b, logins.get(a), logins.get(b), handles.get(a), handles.get(b))

    buckets.clear()
    user_campuses.clear()
    user_handles.clear()
    user_logins.clear()

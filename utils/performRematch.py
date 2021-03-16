import random
from collections import deque
from typing import Deque, Dict

from telegram import ParseMode
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
    CALLBACK_ACTIVE_YES,
    USER_DATA_V1_AUTHORIZED,
    USER_DATA_V1_SETTINGS_CAMPUS,
)
from config.env import ADMIN_IDS
from utils.getters import get_bucket
from utils.performMatch import match


def perform_rematch(ctx: CallbackContext) -> None:
    buckets: Dict[str, Deque] = {
        CALLBACK_CAMPUS_KAZAN: deque(),
        CALLBACK_CAMPUS_MOSCOW: deque(),
        'online': deque(),
        '???': deque(),
    }
    user_campuses = {}
    user_buckets = {}
    user_handles = {}
    user_logins = {}

    for uid, udata in ctx.dispatcher.user_data.items():
        if not udata.get(USER_DATA_V1_AUTHORIZED, False):
            udata[USER_DATA_V1_AUTHORIZED] = False
            continue

        if udata.get(USER_DATA_V1_SETTINGS_ACTIVE, CALLBACK_ACTIVE_NO) != CALLBACK_ACTIVE_YES:
            udata[USER_DATA_V1_SETTINGS_ACTIVE] = CALLBACK_ACTIVE_NO
            continue

        if udata.get(USER_DATA_V1_MATCH_WITH, None) and not udata[USER_DATA_V1_MATCH_ACCEPTED]:
            bid = udata[USER_DATA_V1_MATCH_WITH]
            bdata = ctx.dispatcher.user_data.get(bid, {})
            if bdata is not None and bdata.get(USER_DATA_V1_MATCH_ACCEPTED, False):
                bdata[USER_DATA_V1_MATCH_ACCEPTED] = False
                bdata[USER_DATA_V1_MATCH_WITH] = None
                try:
                    ctx.bot.send_message(bid, text='К сожалению, твой пир на случайный кофе не подтвердил встречу...\n'
                                                   'Ищем нового!')
                except:
                    # TODO actually handle exception
                    pass
                ctx.bot.send_message(ADMIN_IDS[0], text='`[t#{0:<10}] {2:<8}` @{1} <= apology'.format(
                    bid,
                    bdata.get(USER_DATA_V1_TELEGRAM_USERNAME, '???').replace('_', '\\_'),
                    bdata[USER_DATA_V1_INTRA_LOGIN]
                ), parse_mode=ParseMode.MARKDOWN)

            udata[USER_DATA_V1_SETTINGS_ACTIVE] = CALLBACK_ACTIVE_NO
            udata[USER_DATA_V1_MATCH_ACCEPTED] = False
            udata[USER_DATA_V1_MATCH_WITH] = None
            try:
                ctx.bot.send_message(uid, text='К сожалению, ты не подтвердил встречу... '
                                               'Автоматически выставляю тебе статус inactive.\n'
                                               'Ждем тебя, когда вновь появится время на случайный кофе!')
            except:
                # TODO actually handle exception
                pass
            ctx.bot.send_message(ADMIN_IDS[0], text='`[t#{0:<10}] {2:<8}` @{1} <= inactive'.format(
                uid,
                udata.get(USER_DATA_V1_TELEGRAM_USERNAME, '???').replace('_', '\\_'),
                udata[USER_DATA_V1_INTRA_LOGIN]
            ), parse_mode=ParseMode.MARKDOWN)

    for uid, udata in ctx.dispatcher.user_data.items():
        if not udata.get(USER_DATA_V1_AUTHORIZED, False):
            udata[USER_DATA_V1_AUTHORIZED] = False
            continue

        if udata.get(USER_DATA_V1_SETTINGS_ACTIVE, CALLBACK_ACTIVE_NO) != CALLBACK_ACTIVE_YES:
            udata[USER_DATA_V1_SETTINGS_ACTIVE] = CALLBACK_ACTIVE_NO
            continue

        if udata.get(USER_DATA_V1_MATCH_WITH, None):
            continue

        bucket = get_bucket(udata)
        user_buckets[uid] = bucket

        handle = udata.get(USER_DATA_V1_TELEGRAM_USERNAME, '???')
        user_handles[uid] = handle

        login = udata.get(USER_DATA_V1_INTRA_LOGIN, '???')
        user_logins[uid] = login

        campus = udata.get(USER_DATA_V1_SETTINGS_CAMPUS, '???')
        user_campuses[uid] = campus

        buckets[bucket].append(uid)

    for bucket, uids in buckets.items():
        random.shuffle(uids)

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
            abucket = user_buckets[a]
            acampus = user_campuses[a]
            b = uids.pop()
            bbucket = user_buckets[a]
            bcampus = user_campuses[b]

            if (abucket != acampus or bbucket != bcampus) and \
                    abucket != 'online' and \
                    abucket != 'online' and \
                    acampus != bcampus:
                tmp = [b]

                while acampus != bcampus and uids:
                    c = uids.pop()
                    ccampus = user_campuses[c]

                    if acampus != ccampus:
                        tmp.append(c)
                    else:
                        uids.extendleft(tmp)
                        tmp.clear()
                        b = c
                        bcampus = ccampus

                if tmp:
                    uids.extendleft(tmp)
                    tmp.clear()

            match(ctx, a, b, user_logins.get(a), user_logins.get(b), user_handles.get(a), user_handles.get(b))

        if not uids:
            continue

        if bucket != 'online':
            last = uids.pop()
            buckets['online'].appendleft(last)

        # TODO reimplement saviour mechanic
        # if bucket == 'online':
        #     a = uids.pop()
        #     b = SAVIOUR_ID
        #     match(ctx, a, b, logins.get(a), logins.get(b), handles.get(a), handles.get(b))

    buckets.clear()
    user_campuses.clear()
    user_buckets.clear()
    user_handles.clear()
    user_logins.clear()

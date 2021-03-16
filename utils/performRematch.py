import random

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
)
from config.env import SAVIOUR_ID, ADMIN_IDS
from utils.getters import get_bucket
from utils.performMatch import match


def perform_rematch(ctx: CallbackContext) -> None:
    buckets = {
        CALLBACK_CAMPUS_KAZAN: [],
        CALLBACK_CAMPUS_MOSCOW: [],
        'online': [],
        '???': [],
    }
    handles = {}
    logins = {}

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
                ctx.bot.send_message(ADMIN_IDS[0], text='[t#{}] {} <= apology'.format(
                    bdata[USER_DATA_V1_TELEGRAM_USERNAME],
                    bdata[USER_DATA_V1_INTRA_LOGIN]
                ))

            udata[USER_DATA_V1_SETTINGS_ACTIVE] = CALLBACK_ACTIVE_NO
            udata[USER_DATA_V1_MATCH_ACCEPTED] = False
            udata[USER_DATA_V1_MATCH_WITH] = None
            try:
                ctx.bot.send_message(bid, text='К сожалению, ты не подтвердил встречу... '
                                               'Автоматически выставляю тебе статус inactive.\n'
                                               'Ждем тебя, когда вновь появится время на случайный кофе!')
            except:
                # TODO actually handle exception
                pass
            ctx.bot.send_message(ADMIN_IDS[0], text='[t#{}] {} <= inactive'.format(
                bdata[USER_DATA_V1_TELEGRAM_USERNAME],
                bdata[USER_DATA_V1_INTRA_LOGIN]
            ))

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

        handle = udata.get(USER_DATA_V1_TELEGRAM_USERNAME, '???')
        handles[uid] = handle

        login = udata.get(USER_DATA_V1_INTRA_LOGIN, '???')
        logins[uid] = login

        buckets[bucket].append(uid)

    for bucket, uids in buckets.items():
        if bucket == '???':
            if uids:
                ctx.bot.send_message(
                    ADMIN_IDS[0],
                    text='For some reason ??? bucket has #{} accounts in it'.format(len(uids))
                )
            continue

        random.shuffle(uids)
        while len(uids) > 1:
            a = uids.pop()
            b = uids.pop()
            match(ctx, a, b, logins.get(a), logins.get(b), handles.get(a), handles.get(b))

        if not uids:
            continue

        if bucket != 'online':
            last = uids.pop()
            buckets['online'].append(last)

        if bucket == 'online':
            a = uids.pop()
            b = SAVIOUR_ID
            match(ctx, a, b, logins.get(a), logins.get(b), handles.get(a), handles.get(b))

    buckets.clear()
    handles.clear()
    logins.clear()

import random

from telegram.ext import CallbackContext, PicklePersistence

from config.constants import USER_DATA_CAMPUS, USER_DATA_ONLINE, CALLBACK_CAMPUS_KAZAN, CALLBACK_CAMPUS_MOSCOW, \
    USER_DATA_TELEGRAM_USERNAME, USER_DATA_LOGIN
from config.env import SAVIOUR_ID


def send_match_message(ctx: CallbackContext, fromid: int, tologin: str, tohandle: str) -> None:
    ctx.bot.send_message(
        fromid,
        text='Твой случайный кофе на этой неделе...\nC пиром {} [tg: @{}]!'.format(
            tologin,
            tohandle
        )
    )


def send_match_messages(ctx: CallbackContext, aid: int, bid: int, alogin: str, blogin: str, ahandle: str,
                        bhandle: str) -> None:
    send_match_message(ctx, aid, blogin, bhandle)
    send_match_message(ctx, bid, alogin, ahandle)


def perform_match_job(ctx: CallbackContext) -> None:
    persistence: PicklePersistence = ctx.job.context
    perform_match(ctx, persistence)


def perform_match(ctx: CallbackContext, persistence: PicklePersistence) -> None:
    buckets = {
        CALLBACK_CAMPUS_KAZAN: [],
        CALLBACK_CAMPUS_MOSCOW: [],
        'online': []
    }
    handles = {}
    logins = {}

    for id, person in persistence.user_data.items():
        campus = person.get(USER_DATA_CAMPUS)
        online = person.get(USER_DATA_ONLINE)

        handle = person.get(USER_DATA_TELEGRAM_USERNAME)
        handles[id] = handle

        login = person.get(USER_DATA_LOGIN)
        logins[id] = login

        if online:
            buckets['online'].append(id)
        else:
            buckets[campus].append(id)

    for campus, bucket in buckets.items():
        random.shuffle(bucket)
        while len(bucket) > 1:
            a = bucket.pop()
            b = bucket.pop()
            send_match_messages(ctx, a, b, logins.get(a), logins.get(b), handles.get(a), handles.get(b))

        if campus != 'online' and bucket:
            last = bucket.pop()
            buckets['online'].append(last)

        if campus == 'online':
            a = bucket.pop()
            b = SAVIOUR_ID
            send_match_messages(ctx, a, b, logins.get(a), logins.get(b), handles.get(a), handles.get(b))

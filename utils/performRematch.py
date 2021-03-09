import random

from telegram.ext import CallbackContext

from config.constants import USER_DATA_CAMPUS, USER_DATA_ONLINE, CALLBACK_CAMPUS_KAZAN, CALLBACK_CAMPUS_MOSCOW, \
    USER_DATA_TELEGRAM_USERNAME, USER_DATA_LOGIN, USER_DATA_ACCEPTED, USER_DATA_MATCHED_WITH, USER_DATA_ACTIVE, \
    CALLBACK_ACTIVE_NO
from config.env import SAVIOUR_ID
from utils.performMatch import match


def perform_rematch(ctx: CallbackContext) -> None:
    buckets = {
        CALLBACK_CAMPUS_KAZAN: [],
        CALLBACK_CAMPUS_MOSCOW: [],
        'online': []
    }
    handles = {}
    logins = {}

    for id, person in ctx.dispatcher.user_data.items():
        active = person.get(USER_DATA_ACTIVE)
        if active == CALLBACK_ACTIVE_NO:
            continue

        accepted = person.get(USER_DATA_ACCEPTED)
        if not accepted:
            person[USER_DATA_ACTIVE] = CALLBACK_ACTIVE_NO

    for id, person in ctx.dispatcher.user_data.items():
        accepted = person.get(USER_DATA_ACCEPTED)
        peer = person.get(USER_DATA_MATCHED_WITH)
        peer_active = ctx.dispatcher.user_data[peer][USER_DATA_ACTIVE]

        if not accepted or peer_active:
            continue

        ctx.bot.send_message(id, text='К сожалению, твой пир на случайный кофе не подтвердил встречу... Ищем нового!')

        # FIXME lower code duplication
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

    # FIXME lower code duplication
    for campus, bucket in buckets.items():
        random.shuffle(bucket)
        while len(bucket) > 1:
            a = bucket.pop()
            b = bucket.pop()
            match(ctx, a, b, logins.get(a), logins.get(b), handles.get(a), handles.get(b))

        if campus != 'online' and bucket:
            last = bucket.pop()
            buckets['online'].append(last)

        if campus == 'online':
            a = bucket.pop()
            b = SAVIOUR_ID
            match(ctx, a, b, logins.get(a), logins.get(b), handles.get(a), handles.get(b))

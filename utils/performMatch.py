import logging
import random

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from config.constants import (
    USER_DATA_V1_SETTINGS_CAMPUS,
    USER_DATA_V1_SETTINGS_ONLINE,
    CALLBACK_CAMPUS_KAZAN,
    CALLBACK_CAMPUS_MOSCOW,
    USER_DATA_V1_TELEGRAM_USERNAME,
    USER_DATA_V1_INTRA_LOGIN,
    USER_DATA_V1_MATCH_ACCEPTED,
    USER_DATA_V1_MATCH_WITH,
    USER_DATA_V1_SETTINGS_ACTIVE,
    CALLBACK_ACTIVE_NO,
    CALLBACK_ONLINE_NO,
)
from config.env import SAVIOUR_ID


def send_match_message(ctx: CallbackContext, fromid: int, tologin: str, tohandle: str) -> None:
    kbd = [
        [
            InlineKeyboardButton('Подтвердить встречу', callback_data='match-accept')
        ]
    ]

    ctx.bot.send_message(
        fromid,
        text='Твой случайный кофе на этой неделе...\nC пиром {} [tg: @{}]!'.format(
            tologin,
            tohandle
        ),
        reply_markup=InlineKeyboardMarkup(kbd)
    )


def match(ctx: CallbackContext, aid: int, bid: int, alogin: str, blogin: str, ahandle: str, bhandle: str) -> None:
    ctx.dispatcher.user_data[aid][USER_DATA_V1_MATCH_ACCEPTED] = False
    ctx.dispatcher.user_data[aid][USER_DATA_V1_MATCH_WITH] = bid
    ctx.dispatcher.user_data[bid][USER_DATA_V1_MATCH_ACCEPTED] = False
    ctx.dispatcher.user_data[bid][USER_DATA_V1_MATCH_WITH] = aid
    # send_match_message(ctx, aid, blogin, bhandle)
    # send_match_message(ctx, bid, alogin, ahandle)


def perform_match(ctx: CallbackContext) -> None:
    buckets = {
        CALLBACK_CAMPUS_KAZAN: [],
        CALLBACK_CAMPUS_MOSCOW: [],
        'online': [],
        '???': []
    }
    handles = {}
    logins = {}

    for id, person in ctx.dispatcher.user_data.items():
        active = person.get(USER_DATA_V1_SETTINGS_ACTIVE, CALLBACK_ACTIVE_NO)
        if active == CALLBACK_ACTIVE_NO:
            continue

        campus = person.get(USER_DATA_V1_SETTINGS_CAMPUS, '???')
        online = person.get(USER_DATA_V1_SETTINGS_ONLINE, CALLBACK_ONLINE_NO)

        handle = person.get(USER_DATA_V1_TELEGRAM_USERNAME, '???')
        handles[id] = handle

        login = person.get(USER_DATA_V1_INTRA_LOGIN, '???')
        logins[id] = login

        if online:
            buckets['online'].append(id)
        else:
            buckets[campus].append(id)

    for campus, bucket in buckets.items():
        if campus == '???':
            if bucket:
                logging.error('For some reason ??? bucket has #{} accounts in it'.format(len(bucket)))
            continue

        random.shuffle(bucket)
        while len(bucket) > 1:
            a = bucket.pop()
            b = bucket.pop()
            match(ctx, a, b, logins.get(a), logins.get(b), handles.get(a), handles.get(b))

        if campus != 'online' and bucket:
            last = bucket.pop()
            buckets['online'].append(last)

        if campus == 'online' and bucket:
            a = bucket.pop()
            b = SAVIOUR_ID
            match(ctx, a, b, logins.get(a), logins.get(b), handles.get(a), handles.get(b))

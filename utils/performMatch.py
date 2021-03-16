import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, TelegramError
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
)
from config.env import SAVIOUR_ID, ADMIN_IDS
from handlers.error import send_error
from utils.getters import get_bucket


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
    ctx.dispatcher.user_data[aid][USER_DATA_V1_MATCH_WITH] = bid
    ctx.dispatcher.user_data[bid][USER_DATA_V1_MATCH_WITH] = aid
    send_match_message(ctx, aid, blogin, bhandle)
    send_match_message(ctx, bid, alogin, ahandle)


def perform_match(ctx: CallbackContext) -> None:
    buckets = {
        CALLBACK_CAMPUS_KAZAN: [],
        CALLBACK_CAMPUS_MOSCOW: [],
        'online': [],
        '???': [],
    }
    handles = {}
    logins = {}

    for uid, udata in ctx.dispatcher.user_data.items():
        udata[USER_DATA_V1_MATCH_ACCEPTED] = False
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
                    ctx.bot.send_message(ADMIN_IDS[0], text='[t#{}] {} <= removed due to being blocked'.format(
                        udata[USER_DATA_V1_TELEGRAM_USERNAME],
                        udata[USER_DATA_V1_INTRA_LOGIN]
                    ))
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

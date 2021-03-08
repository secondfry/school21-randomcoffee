from telegram.ext import CallbackContext

from config.constants import USER_DATA_ACCEPTED, USER_DATA_LOGIN, USER_DATA_TELEGRAM_USERNAME


def check_pair(context: CallbackContext, aid: int, bid: int):
    return context.dispatcher.user_data.get(aid).get(USER_DATA_ACCEPTED) \
           and context.dispatcher.user_data.get(bid).get(USER_DATA_ACCEPTED)


def notify_user(context: CallbackContext, toid: int, peerlogin: str, peerhandle: str):
    context.bot.send_message(
        toid,
        text='И ты, и {} [tg: @{}] подтвердили встречу! :)'.format(peerlogin, peerhandle)
    )


def notify_pair(context: CallbackContext, aid: int, bid: int):
    a = context.dispatcher.user_data.get(aid)
    b = context.dispatcher.user_data.get(bid)
    notify_user(context, aid, b.get(USER_DATA_LOGIN), b.get(USER_DATA_TELEGRAM_USERNAME))
    notify_user(context, bid, a.get(USER_DATA_LOGIN), a.get(USER_DATA_TELEGRAM_USERNAME))

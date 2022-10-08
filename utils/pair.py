from config.constants import KEY_MATCH_ACCEPTED, KEY_TELEGRAM_USERNAME, KEY_USER_ID
from telegram import ext as telegram_ext


def check_pair(ctx: telegram_ext.CallbackContext, aid: int, bid: int):
    return ctx.application.user_data.get(aid, {}).get(
        KEY_MATCH_ACCEPTED, False
    ) and ctx.application.user_data.get(bid, {}).get(KEY_MATCH_ACCEPTED, False)


async def notify_user(
    context: telegram_ext.CallbackContext, toid: int, peerlogin: str, peerhandle: str
):
    try:
        await context.bot.send_message(
            toid,
            text="И ты, и {} [tg: @{}] подтвердили встречу! :)".format(
                peerlogin, peerhandle
            ),
        )
    except:
        # TODO actually handle exception
        pass


async def notify_pair(ctx: telegram_ext.CallbackContext, aid: int, bid: int):
    a = ctx.application.user_data.get(aid, {})
    b = ctx.application.user_data.get(bid, {})
    await notify_user(
        ctx,
        aid,
        b.get(KEY_USER_ID, "???"),
        b.get(KEY_TELEGRAM_USERNAME, "???"),
    )
    await notify_user(
        ctx,
        bid,
        a.get(KEY_USER_ID, "???"),
        a.get(KEY_TELEGRAM_USERNAME, "???"),
    )

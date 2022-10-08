import telegram
from config.constants import (
    CALLBACK_ACTIVE_NO,
    KEY_AUTHORIZED,
    KEY_MATCH_ACCEPTED,
    KEY_MATCH_WITH,
    KEY_SETTINGS_ACTIVE,
    KEY_SETTINGS_CAMPUS,
    KEY_USER_ID,
)
from config.env import ADMIN_IDS
from telegram import constants as telegram_constants
from telegram import ext as telegram_ext
from utils.getters import get_accepted_sign, get_bucket


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


async def perform_dump(ctx: telegram_ext.CallbackContext, target_uid: int) -> None:
    data_perfect = []
    data_ok = []
    data_nok = []
    data_notmatched = []
    data_inactive = []

    for aid, adata in ctx.application.user_data.items():
        if not adata.get(KEY_AUTHORIZED, False):
            continue

        abucket = get_bucket(adata)
        acampus = adata.get(KEY_SETTINGS_CAMPUS, "???")
        if abucket != acampus:
            abucket = "{}{}".format(abucket[0:3], acampus[0:3])
        alogin = adata.get(KEY_USER_ID, "unset")

        if adata.get(KEY_SETTINGS_ACTIVE, CALLBACK_ACTIVE_NO) == CALLBACK_ACTIVE_NO:
            message = "[{:<6}] {:<8}".format(
                abucket,
                alogin,
            )
            data_inactive.append(message)
            continue

        if not adata.get(KEY_MATCH_WITH, None):
            message = "[{:<6}] {:<8}".format(
                abucket,
                alogin,
            )
            data_notmatched.append(message)
            continue

        bid = adata[KEY_MATCH_WITH]
        bdata = ctx.application.user_data[bid]
        bbucket = get_bucket(bdata)
        bcampus = bdata.get(KEY_SETTINGS_CAMPUS, "???")
        if bbucket != bcampus:
            bbucket = "{}{}".format(bbucket[0:3], bcampus[0:3])
        blogin = bdata.get(KEY_USER_ID, "unset")
        asign = get_accepted_sign(adata)
        bsign = get_accepted_sign(bdata)
        message = "[{1:<6}] {2:<8} {0}|{3} {5:<8} [{4:<6}]".format(
            asign,
            abucket,
            alogin,
            bsign,
            bbucket,
            blogin,
        )

        if abucket[0:3] != bbucket[0:3]:
            data_nok.append(message)
        else:
            if asign != bsign or asign == bsign == get_accepted_sign(
                {KEY_MATCH_ACCEPTED: False}
            ):
                data_ok.append(message)
            else:
                data_perfect.append(message)

    data_perfect.sort()
    data_ok.sort()
    data_nok.sort()
    data_notmatched.sort()
    data_inactive.sort()

    for (name, lst) in [
        ("Отличные пары", data_perfect),
        ("Хорошие пары", data_ok),
        ("Плохие пары", data_nok),
        ("Еще не успели сматчиться", data_notmatched),
        ("Инактив", data_inactive),
    ]:
        if not lst:
            continue
        await ctx.bot.send_message(target_uid, text=name)
        for chunk in chunks(lst, 30):
            message = "```\n{}\n```".format("\n".join(chunk))
            await ctx.bot.send_message(
                target_uid,
                text=message,
                parse_mode=telegram_constants.ParseMode.MARKDOWN,
            )


async def handler_command_dump(
    upd: telegram.Update, ctx: telegram_ext.CallbackContext
) -> None:
    if upd.effective_user.id not in ADMIN_IDS:
        return

    await perform_dump(ctx, upd.effective_user.id)

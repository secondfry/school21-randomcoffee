from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from config.constants import (
    USER_DATA_V1_INTRA_LOGIN,
    USER_DATA_V1_MATCH_WITH,
    USER_DATA_V1_AUTHORIZED,
    USER_DATA_V1_SETTINGS_ACTIVE,
    CALLBACK_ACTIVE_NO,
    USER_DATA_V1_MATCH_ACCEPTED,
)
from config.env import ADMIN_IDS
from utils.getters import get_bucket, get_accepted_sign


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def handler_command_dump(upd: Update, ctx: CallbackContext) -> None:
    if upd.effective_user.id not in ADMIN_IDS:
        return

    data_perfect = []
    data_ok = []
    data_nok = []
    data_notmatched = []
    data_inactive = []

    for aid, adata in ctx.dispatcher.user_data.items():
        if USER_DATA_V1_AUTHORIZED not in adata or not adata[USER_DATA_V1_AUTHORIZED]:
            continue

        abucket = get_bucket(adata)
        alogin = adata.get(USER_DATA_V1_INTRA_LOGIN, 'unset')

        if USER_DATA_V1_SETTINGS_ACTIVE not in adata or adata[USER_DATA_V1_SETTINGS_ACTIVE] == CALLBACK_ACTIVE_NO:
            message = '[{:>9}] {:>10}'.format(
                abucket,
                alogin,
            )
            data_inactive.append(message)
            continue

        if USER_DATA_V1_MATCH_WITH not in adata or not adata[USER_DATA_V1_MATCH_WITH]:
            message = '[{:>9}] {:>10}'.format(
                abucket,
                alogin,
            )
            data_notmatched.append(message)
            continue

        bid = adata[USER_DATA_V1_MATCH_WITH]
        bdata = ctx.dispatcher.user_data[bid]
        bbucket = get_bucket(bdata)
        blogin = bdata.get(USER_DATA_V1_INTRA_LOGIN, 'unset')
        asign = get_accepted_sign(adata)
        bsign = get_accepted_sign(bdata)
        message = '[{}][{:>9}] {:>10} - [{}][{:>9}] {:>10}'.format(
            asign,
            abucket,
            alogin,
            bsign,
            bbucket,
            blogin,
        )

        if abucket != bbucket:
            data_nok.append(message)
        else:
            if asign != bsign or asign == bsign == get_accepted_sign({USER_DATA_V1_MATCH_ACCEPTED: False}):
                data_ok.append(message)
            else:
                data_perfect.append(message)

    data_perfect.sort()
    data_ok.sort()
    data_nok.sort()
    data_notmatched.sort()
    data_inactive.sort()

    for (name, lst) in [
        ('Отличные пары', data_perfect),
        ('Хорошие пары', data_ok),
        ('Плохие пары', data_nok),
        ('Еще не успели сматчиться', data_notmatched),
        ('Инактив', data_inactive)
    ]:
        if not lst:
            continue
        ctx.bot.send_message(upd.effective_user.id, text=name)
        for chunk in chunks(lst, 25):
            message = '```\n{}\n```'.format('\n'.join(chunk))
            ctx.bot.send_message(upd.effective_user.id, text=message, parse_mode=ParseMode.MARKDOWN)

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from config.constants import (
    USER_DATA_V1_INTRA_LOGIN,
    USER_DATA_V1_MATCH_WITH,
    USER_DATA_V1_AUTHORIZED,
    USER_DATA_V1_SETTINGS_ACTIVE,
    CALLBACK_ACTIVE_NO,
)
from config.env import ADMIN_IDS
from utils.getters import get_bucket


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def handler_command_dump(upd: Update, ctx: CallbackContext) -> None:
    if upd.effective_user.id not in ADMIN_IDS:
        return

    data_ok = []
    data_nok = []

    for aid, adata in ctx.dispatcher.user_data.items():
        if USER_DATA_V1_AUTHORIZED not in adata or not adata[USER_DATA_V1_AUTHORIZED]:
            continue

        if USER_DATA_V1_MATCH_WITH not in adata:
            continue

        if USER_DATA_V1_SETTINGS_ACTIVE not in adata or adata[USER_DATA_V1_SETTINGS_ACTIVE] == CALLBACK_ACTIVE_NO:
            continue

        bid = adata[USER_DATA_V1_MATCH_WITH]
        bdata = ctx.dispatcher.user_data[bid]
        abucket = get_bucket(adata)
        bbucket = get_bucket(bdata)
        message = '[{:>9}] {:>10} - [{:>9}] {:>10}'.format(
            abucket,
            adata.get(USER_DATA_V1_INTRA_LOGIN, 'unset'),
            bbucket,
            bdata.get(USER_DATA_V1_INTRA_LOGIN, 'unset'),
        )

        if abucket != bbucket:
            data_nok.append(message)
        else:
            data_ok.append(message)

    data_ok.sort()
    data_nok.sort()

    for lst in [data_ok, data_nok]:
        for chunk in chunks(lst, 25):
            message = '```\n{}\n```'.format('\n'.join(chunk))
            ctx.bot.send_message(upd.effective_user.id, text=message, parse_mode=ParseMode.MARKDOWN)

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from config.constants import (
    USER_DATA_V1_INTRA_LOGIN,
    USER_DATA_V1_SETTINGS_CAMPUS,
    USER_DATA_V1_SETTINGS_ONLINE,
    USER_DATA_V1_MATCH_WITH,
    CALLBACK_ONLINE_YES,
)
from config.env import ADMIN_IDS


def handler_command_dump(upd: Update, ctx: CallbackContext) -> None:
    if upd.effective_user.id not in ADMIN_IDS:
        return

    data = '```\n' + '\n'.join(['[{:>9}] {:>10} - [{:>9}] {:>10}'.format(
        'online' if tdata.get(USER_DATA_V1_SETTINGS_ONLINE, 'no') == CALLBACK_ONLINE_YES else tdata.get(
            USER_DATA_V1_SETTINGS_CAMPUS, 'unset'),
        tdata.get(USER_DATA_V1_INTRA_LOGIN, 'unset'),
        'online' if ctx.dispatcher.user_data.get(tdata.get(USER_DATA_V1_MATCH_WITH, 0),
                                                 {USER_DATA_V1_SETTINGS_CAMPUS: 'undefined'}).get(
            USER_DATA_V1_SETTINGS_ONLINE, 'no') == CALLBACK_ONLINE_YES else ctx.dispatcher.user_data.get(
            tdata.get(USER_DATA_V1_MATCH_WITH, 0), {USER_DATA_V1_SETTINGS_CAMPUS: 'undefined'}).get(
            USER_DATA_V1_SETTINGS_CAMPUS, 'unset'),
        ctx.dispatcher.user_data.get(tdata.get(USER_DATA_V1_MATCH_WITH, 0), {USER_DATA_V1_INTRA_LOGIN: 'undefined'}).get(
            USER_DATA_V1_INTRA_LOGIN, 'unset'),
    ) for tid, tdata in ctx.dispatcher.user_data.items()]) + '\n```'

    print(data)

    ctx.bot.send_message(upd.effective_user.id, text=data, parse_mode=ParseMode.MARKDOWN)

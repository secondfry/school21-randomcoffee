from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from config.constants import USER_DATA_LOGIN, USER_DATA_CAMPUS, USER_DATA_ONLINE, USER_DATA_MATCHED_WITH, \
    CALLBACK_ONLINE_NO, CALLBACK_ONLINE_YES
from config.env import ADMIN_IDS


def handler_command_dump(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return

    data = '```\n' + '\n'.join(['[{:>9}] {:>10} - [{:>9}] {:>10}'.format(
        'online' if tdata.get(USER_DATA_ONLINE, 'no') == CALLBACK_ONLINE_YES else tdata.get(USER_DATA_CAMPUS, 'unset'),
        tdata.get(USER_DATA_LOGIN, 'unset'),
        'online' if context.dispatcher.user_data.get(tdata.get(USER_DATA_MATCHED_WITH, 0), {USER_DATA_CAMPUS: 'undefined'}).get(USER_DATA_ONLINE, 'no') == CALLBACK_ONLINE_YES else context.dispatcher.user_data.get(tdata.get(USER_DATA_MATCHED_WITH, 0), {USER_DATA_CAMPUS: 'undefined'}).get(USER_DATA_CAMPUS, 'unset'),
        context.dispatcher.user_data.get(tdata.get(USER_DATA_MATCHED_WITH, 0), {USER_DATA_LOGIN: 'undefined'}).get(USER_DATA_LOGIN, 'unset'),
    ) for tid, tdata in context.dispatcher.user_data.items()]) + '\n```'

    print(data)

    context.bot.send_message(update.effective_user.id, text=data, parse_mode=ParseMode.MARKDOWN_V2)

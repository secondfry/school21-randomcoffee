from config.constants import (CALLBACK_ACTIVE_NO, CALLBACK_ACTIVE_YES,
                              USER_DATA_V1_AUTHORIZED,
                              USER_DATA_V1_INTRA_LOGIN,
                              USER_DATA_V1_SETTINGS_ACTIVE)
from config.env import ADMIN_IDS
from telegram import ParseMode, Update
from telegram.ext import CallbackContext
from utils.getters import get_accepted_sign

from handlers.commandDump import chunks, perform_dump


def handler_command_forceactive(upd: Update, ctx: CallbackContext):
    if upd.effective_user.id not in ADMIN_IDS:
        return

    activated = []

    for uid, udata in ctx.dispatcher.user_data.items():
        # Not authorized – skip
        if not udata.get(USER_DATA_V1_AUTHORIZED, False):
            udata[USER_DATA_V1_AUTHORIZED] = False
            continue

        # Active – skip
        if udata.get(USER_DATA_V1_SETTINGS_ACTIVE, CALLBACK_ACTIVE_NO) == CALLBACK_ACTIVE_YES:
            continue

        udata[USER_DATA_V1_SETTINGS_ACTIVE] = CALLBACK_ACTIVE_YES
        activated.append('[{2}] {1:<8} [t#{0:<10}]'.format(
            uid,
            udata[USER_DATA_V1_INTRA_LOGIN],
            get_accepted_sign(udata),
        ))

        try:
            ctx.bot.send_message(
                uid,
                text='Привет!\n\n'
                     'В качестве эксперимента на этой неделе все пользователи становятся активными! '
                     'Ато вдруг ты хотел сходить на кофе, но опять забыл или еще чего ;).\n\n'
                     'P.S. Ты можешь обратно стать неактивным при помощи настроек /settings')
        except Exception as e:
            ctx.bot.send_message(ADMIN_IDS[0], text='{}'.format(e))

    activated.sort()
    ctx.bot.send_message(ADMIN_IDS[0], text='Активированы')
    for chunk in chunks(activated, 30):
        ctx.bot.send_message(ADMIN_IDS[0], text='```\n{}\n```'.format('\n'.join(chunk)), parse_mode=ParseMode.MARKDOWN)

    perform_dump(ctx, ADMIN_IDS[0])

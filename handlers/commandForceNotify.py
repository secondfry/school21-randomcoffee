from telegram import Update, ParseMode
from telegram.error import TelegramError
from telegram.ext import CallbackContext

from config.constants import (
    USER_DATA_V1_AUTHORIZED,
    USER_DATA_V1_SETTINGS_ACTIVE,
    CALLBACK_ACTIVE_NO,
    CALLBACK_ACTIVE_YES,
    USER_DATA_V1_MATCH_ACCEPTED,
    USER_DATA_V1_MATCH_WITH,
    USER_DATA_V1_INTRA_LOGIN,
    USER_DATA_V1_TELEGRAM_USERNAME,
)
from config.env import ADMIN_IDS
from handlers.commandDump import chunks
from handlers.error import handle_common_block_errors, send_error
from utils.getters import get_accepted_sign
from utils.performMatch import send_match_message


def handler_command_forcenotify(upd: Update, ctx: CallbackContext):
    if upd.effective_user.id not in ADMIN_IDS:
        return

    notified = []

    for uid, udata in ctx.dispatcher.user_data.items():
        # Not authorized – skip
        if not udata.get(USER_DATA_V1_AUTHORIZED, False):
            udata[USER_DATA_V1_AUTHORIZED] = False
            continue

        # Not active – skip
        if udata.get(USER_DATA_V1_SETTINGS_ACTIVE, CALLBACK_ACTIVE_NO) != CALLBACK_ACTIVE_YES:
            udata[USER_DATA_V1_SETTINGS_ACTIVE] = CALLBACK_ACTIVE_NO
            continue

        # Have already accepted match – skip
        if udata.get(USER_DATA_V1_MATCH_ACCEPTED, False):
            continue

        # Has no match to accept – skip
        bid = udata.get(USER_DATA_V1_MATCH_WITH, None)
        if not bid:
            continue

        # Match is not authorized – set accepted to true
        bdata = ctx.dispatcher.user_data.get(bid, {})
        if not bdata.get(USER_DATA_V1_AUTHORIZED, False):
            bdata[USER_DATA_V1_AUTHORIZED] = False
            udata[USER_DATA_V1_MATCH_ACCEPTED] = True
            continue

        # Match is not active – set accepted to true
        if bdata.get(USER_DATA_V1_SETTINGS_ACTIVE, CALLBACK_ACTIVE_NO) != CALLBACK_ACTIVE_YES:
            bdata[USER_DATA_V1_SETTINGS_ACTIVE] = CALLBACK_ACTIVE_NO
            udata[USER_DATA_V1_MATCH_ACCEPTED] = True
            continue

        notified.append('[{2}] {1:<8} [t#{0:<10}]'.format(
            uid,
            udata[USER_DATA_V1_INTRA_LOGIN],
            get_accepted_sign(udata),
        ))
        try:
            ctx.bot.send_message(uid, text='Ой-ой-ой, я запутался кому отправлял уведомления, а кому нет. Не серчай!\n'
                                           'P.S. Если получение матча не подтвердить, '
                                           'то бот автоматически сделает тебя неактивным.')
        except TelegramError as ex:
            if not handle_common_block_errors(ctx, uid, ex):
                send_error(ctx, uid, udata[USER_DATA_V1_TELEGRAM_USERNAME], udata[USER_DATA_V1_INTRA_LOGIN],
                           'Can\'t send force active message.', ex)
        except Exception as ex:
            send_error(ctx, uid, udata[USER_DATA_V1_TELEGRAM_USERNAME], udata[USER_DATA_V1_INTRA_LOGIN],
                       'Can\'t send force active message.', ex)
        send_match_message(
            ctx,
            uid,
            bdata.get(USER_DATA_V1_INTRA_LOGIN, '???'),
            bdata.get(USER_DATA_V1_TELEGRAM_USERNAME, '???')
        )

    notified.sort()
    ctx.bot.send_message(ADMIN_IDS[0], text='Уведомлены')
    for chunk in chunks(notified, 30):
        ctx.bot.send_message(ADMIN_IDS[0], text='```\n{}\n```'.format('\n'.join(chunk)), parse_mode=ParseMode.MARKDOWN)

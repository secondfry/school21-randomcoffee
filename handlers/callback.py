import telegram
from config.constants import (
    CALLBACK_ACTION_MATCH,
    CALLBACK_ACTION_SETTING,
    KEY_AUTHORIZED,
    KEY_MATCH_ACCEPTED,
    KEY_MATCH_WITH,
    KEY_SETTINGS_ACTIVE,
    KEY_SETTINGS_CAMPUS,
    KEY_SETTINGS_ONLINE,
)
from telegram import ext as telegram_ext
from utils.getters import (
    get_accepted,
    get_active_status,
    get_campus_name,
    get_online_status,
)
from utils.lang import COMMAND_DENIED_NOT_AUTHORIZED
from utils.pair import check_pair, notify_pair

from handlers.commandSettings import (
    settings_choose_active,
    settings_choose_online,
    settings_finish,
)


async def set_campus(
    upd: telegram.Update, ctx: telegram_ext.CallbackContext, campus: str
):
    ctx.user_data[KEY_SETTINGS_CAMPUS] = campus

    kbd = [
        [
            telegram.InlineKeyboardButton(
                "✅ {}".format(get_campus_name(campus)), callback_data="none"
            )
        ]
    ]
    await upd.callback_query.edit_message_reply_markup(
        telegram.InlineKeyboardMarkup(kbd)
    )

    await settings_choose_online(ctx, upd.effective_user.id)


async def set_online(
    upd: telegram.Update, ctx: telegram_ext.CallbackContext, online: str
):
    ctx.user_data[KEY_SETTINGS_ONLINE] = online

    kbd = [
        [
            telegram.InlineKeyboardButton(
                "✅ {}".format(get_online_status(online)), callback_data="none"
            )
        ]
    ]
    await upd.callback_query.edit_message_reply_markup(
        telegram.InlineKeyboardMarkup(kbd)
    )

    await settings_choose_active(ctx, upd.effective_user.id)


async def set_active(
    upd: telegram.Update, ctx: telegram_ext.CallbackContext, active: str
):
    ctx.user_data[KEY_SETTINGS_ACTIVE] = active

    kbd = [
        [
            telegram.InlineKeyboardButton(
                "✅ {}".format(get_active_status(active)), callback_data="none"
            )
        ]
    ]
    await upd.callback_query.edit_message_reply_markup(
        telegram.InlineKeyboardMarkup(kbd)
    )

    await settings_finish(ctx, upd.effective_user.id)


async def set_accepted(upd: telegram.Update, ctx: telegram_ext.CallbackContext):
    ctx.user_data[KEY_MATCH_ACCEPTED] = True

    kbd = [
        [
            telegram.InlineKeyboardButton(
                "✅ {}".format(get_accepted()), callback_data="none"
            )
        ]
    ]
    await upd.callback_query.edit_message_reply_markup(
        telegram.InlineKeyboardMarkup(kbd)
    )

    if check_pair(ctx, upd.effective_user.id, ctx.user_data.get(KEY_MATCH_WITH)):
        await notify_pair(ctx, upd.effective_user.id, ctx.user_data.get(KEY_MATCH_WITH))


async def handler_callback(
    upd: telegram.Update, ctx: telegram_ext.CallbackContext
) -> None:
    query = upd.callback_query

    if not ctx.user_data.get(KEY_AUTHORIZED, False):
        await query.answer(text=COMMAND_DENIED_NOT_AUTHORIZED)
        return

    await query.answer()

    req = query.data.split("-")

    if req[0] == CALLBACK_ACTION_SETTING:
        await {"campus": set_campus, "online": set_online, "active": set_active,}.get(
            req[1], lambda: None
        )(upd, ctx, req[2])

        return

    if req[0] == CALLBACK_ACTION_MATCH:
        await {"accept": set_accepted}.get(req[1], lambda: None)(upd, ctx)

        return

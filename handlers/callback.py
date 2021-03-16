from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from config.constants import (
    USER_DATA_V1_SETTINGS_CAMPUS,
    USER_DATA_V1_SETTINGS_ONLINE,
    CALLBACK_ACTION_SETTING,
    CALLBACK_ACTION_MATCH,
    USER_DATA_V1_MATCH_ACCEPTED,
    USER_DATA_V1_MATCH_WITH,
    USER_DATA_V1_SETTINGS_ACTIVE,
    USER_DATA_V1_AUTHORIZED,
)
from handlers.commandSettings import settings_choose_online, settings_finish, settings_choose_active
from utils.getters import get_campus_name, get_online_status, get_accepted, get_active_status
from utils.lang import COMMAND_DENIED_NOT_AUTHORIZED
from utils.pair import check_pair, notify_pair


def set_campus(upd: Update, ctx: CallbackContext, campus: str):
    ctx.user_data[USER_DATA_V1_SETTINGS_CAMPUS] = campus

    kbd = [[InlineKeyboardButton('✅ {}'.format(get_campus_name(campus)), callback_data='none')]]
    upd.callback_query.edit_message_reply_markup(InlineKeyboardMarkup(kbd))

    settings_choose_online(ctx, upd.effective_user.id)


def set_online(upd: Update, ctx: CallbackContext, online: str):
    ctx.user_data[USER_DATA_V1_SETTINGS_ONLINE] = online

    kbd = [[InlineKeyboardButton('✅ {}'.format(get_online_status(online)), callback_data='none')]]
    upd.callback_query.edit_message_reply_markup(InlineKeyboardMarkup(kbd))

    settings_choose_active(ctx, upd.effective_user.id)


def set_active(upd: Update, ctx: CallbackContext, active: str):
    ctx.user_data[USER_DATA_V1_SETTINGS_ACTIVE] = active

    kbd = [[InlineKeyboardButton('✅ {}'.format(get_active_status(active)), callback_data='none')]]
    upd.callback_query.edit_message_reply_markup(InlineKeyboardMarkup(kbd))

    settings_finish(ctx, upd.effective_user.id)


def set_accepted(upd: Update, ctx: CallbackContext):
    ctx.user_data[USER_DATA_V1_MATCH_ACCEPTED] = True

    kbd = [[InlineKeyboardButton('✅ {}'.format(get_accepted()), callback_data='none')]]
    upd.callback_query.edit_message_reply_markup(InlineKeyboardMarkup(kbd))

    if check_pair(ctx, upd.effective_user.id, ctx.user_data.get(USER_DATA_V1_MATCH_WITH)):
        notify_pair(ctx, upd.effective_user.id, ctx.user_data.get(USER_DATA_V1_MATCH_WITH))


def handler_callback(upd: Update, ctx: CallbackContext) -> None:
    query = upd.callback_query

    if not ctx.user_data.get(USER_DATA_V1_AUTHORIZED, False):
        query.answer(text=COMMAND_DENIED_NOT_AUTHORIZED)
        return

    query.answer()

    req = query.data.split('-')

    if req[0] == CALLBACK_ACTION_SETTING:
        {
            'campus': set_campus,
            'online': set_online,
            'active': set_active,
        }.get(req[1], lambda: None)(upd, ctx, req[2])

        return

    if req[0] == CALLBACK_ACTION_MATCH:
        {
            'accept': set_accepted
        }.get(req[1], lambda: None)(upd, ctx)

        return

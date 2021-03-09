from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from config.constants import USER_DATA_CAMPUS, USER_DATA_ONLINE, CALLBACK_ACTION_SETTING, CALLBACK_ACTION_MATCH, \
    USER_DATA_ACCEPTED, USER_DATA_MATCHED_WITH, USER_DATA_ACTIVE
from handlers.commandSettings import settings_choose_online, settings_finish, settings_choose_active
from utils.getters import get_campus_name, get_online_status, get_accepted, get_active_status
from utils.pair import check_pair, notify_pair


def set_campus(update: Update, context: CallbackContext, campus: str):
    context.user_data[USER_DATA_CAMPUS] = campus

    kbd = [[InlineKeyboardButton('✅ {}'.format(get_campus_name(campus)), callback_data='none')]]
    update.callback_query.edit_message_reply_markup(InlineKeyboardMarkup(kbd))

    settings_choose_online(context, update.effective_user.id)


def set_online(update: Update, context: CallbackContext, online: str):
    context.user_data[USER_DATA_ONLINE] = online

    kbd = [[InlineKeyboardButton('✅ {}'.format(get_online_status(online)), callback_data='none')]]
    update.callback_query.edit_message_reply_markup(InlineKeyboardMarkup(kbd))

    settings_choose_active(context, update.effective_user.id)


def set_active(update: Update, context: CallbackContext, active: str):
    context.user_data[USER_DATA_ACTIVE] = active

    kbd = [[InlineKeyboardButton('✅ {}'.format(get_active_status(active)), callback_data='none')]]
    update.callback_query.edit_message_reply_markup(InlineKeyboardMarkup(kbd))

    settings_finish(context, update.effective_user.id)


def set_accepted(update: Update, context: CallbackContext):
    context.user_data[USER_DATA_ACCEPTED] = True

    kbd = [[InlineKeyboardButton('✅ {}'.format(get_accepted()), callback_data='none')]]
    update.callback_query.edit_message_reply_markup(InlineKeyboardMarkup(kbd))

    if check_pair(context, update.effective_user.id, context.user_data.get(USER_DATA_MATCHED_WITH)):
        notify_pair(context, update.effective_user.id, context.user_data.get(USER_DATA_MATCHED_WITH))


def handler_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    req = query.data.split('-')

    if req[0] == CALLBACK_ACTION_SETTING:
        {
            'campus': set_campus,
            'online': set_online,
            'active': set_active,
        }.get(req[1], lambda: None)(update, context, req[2])

        return

    if req[0] == CALLBACK_ACTION_MATCH:
        {
            'accept': set_accepted
        }.get(req[1], lambda: None)(update, context)

        return

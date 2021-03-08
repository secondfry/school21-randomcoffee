from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from config.constants import USER_DATA_CAMPUS, USER_DATA_ONLINE
from handlers.commandSettings import settings_choose_online, settings_finish
from utils.getters import get_campus_name, get_online_status


def set_campus(update: Update, context: CallbackContext, campus: str):
    context.user_data[USER_DATA_CAMPUS] = campus

    kbd = [[InlineKeyboardButton('✅ {}'.format(get_campus_name(campus)), callback_data='none')]]
    update.callback_query.edit_message_reply_markup(InlineKeyboardMarkup(kbd))

    settings_choose_online(context, update.effective_user.id)


def set_online(update: Update, context: CallbackContext, online: str):
    context.user_data[USER_DATA_ONLINE] = online

    kbd = [[InlineKeyboardButton('✅ {}'.format(get_online_status(online)), callback_data='none')]]
    update.callback_query.edit_message_reply_markup(InlineKeyboardMarkup(kbd))

    settings_finish(context, update.effective_user.id)


def handler_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    req = query.data.split('-')

    if req[0] != 'settings':
        return

    {
        'campus': set_campus,
        'online': set_online
    }.get(req[1], lambda: None)(update, context, req[2])

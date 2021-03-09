from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from config.constants import CALLBACK_CHOOSE_KAZAN, CALLBACK_CHOOSE_MOSCOW, CALLBACK_CAMPUS_KAZAN, \
    CALLBACK_CAMPUS_MOSCOW, CALLBACK_CHOOSE_OFFLINE, CALLBACK_CHOOSE_ONLINE, CALLBACK_ONLINE_YES, CALLBACK_ONLINE_NO, \
    CALLBACK_ACTIVE_YES, CALLBACK_ACTIVE_NO, CALLBACK_CHOOSE_ACTIVE, CALLBACK_CHOOSE_INACTIVE
from utils.getters import get_campus_name, get_online_status, get_active_status


def settings_choose_campus(context: CallbackContext, id: int) -> None:
    kbd = [
        [
            InlineKeyboardButton(get_campus_name(CALLBACK_CAMPUS_KAZAN), callback_data=CALLBACK_CHOOSE_KAZAN),
            InlineKeyboardButton(get_campus_name(CALLBACK_CAMPUS_MOSCOW), callback_data=CALLBACK_CHOOSE_MOSCOW),
        ]
    ]

    context.bot.send_message(
        id,
        text='В каком кампусе ты хочешь встречи?',
        reply_markup=InlineKeyboardMarkup(kbd)
    )


def settings_choose_online(context: CallbackContext, id: int) -> None:
    kbd = [
        [
            InlineKeyboardButton(get_online_status(CALLBACK_ONLINE_YES), callback_data=CALLBACK_CHOOSE_ONLINE),
        ],
        [
            InlineKeyboardButton(get_online_status(CALLBACK_ONLINE_NO), callback_data=CALLBACK_CHOOSE_OFFLINE),
        ]
    ]

    context.bot.send_message(
        id,
        text='Готов ли ты к встречам онлайн?',
        reply_markup=InlineKeyboardMarkup(kbd)
    )


def settings_choose_active(context: CallbackContext, id: int) -> None:
    kbd = [
        [
            InlineKeyboardButton(get_active_status(CALLBACK_ACTIVE_YES), callback_data=CALLBACK_CHOOSE_ACTIVE),
        ],
        [
            InlineKeyboardButton(get_active_status(CALLBACK_ACTIVE_NO), callback_data=CALLBACK_CHOOSE_INACTIVE),
        ]
    ]

    context.bot.send_message(
        id,
        text='На этой неделе участвуешь в случайном кофе?',
        reply_markup=InlineKeyboardMarkup(kbd)
    )


def settings_finish(context: CallbackContext, id: int) -> None:
    context.bot.send_message(
        id,
        text='Я запомнил твои предпочтения!\n\nУчти, что они автоматически продляются на все последующие недели, '
             'если ты их не изменишь.'
    )


def handler_command_settings(update: Update, context: CallbackContext) -> None:
    settings_choose_campus(context, update.effective_user.id)

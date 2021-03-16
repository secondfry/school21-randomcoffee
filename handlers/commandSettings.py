from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from config.constants import (
    CALLBACK_CHOOSE_KAZAN,
    CALLBACK_CHOOSE_MOSCOW,
    CALLBACK_CAMPUS_KAZAN,
    CALLBACK_CAMPUS_MOSCOW,
    CALLBACK_CHOOSE_OFFLINE,
    CALLBACK_CHOOSE_ONLINE,
    CALLBACK_ONLINE_YES,
    CALLBACK_ONLINE_NO,
    CALLBACK_ACTIVE_YES,
    CALLBACK_ACTIVE_NO,
    CALLBACK_CHOOSE_ACTIVE,
    CALLBACK_CHOOSE_INACTIVE,
    USER_DATA_V1_AUTHORIZED,
)
from utils.getters import get_campus_name, get_online_status, get_active_status
from utils.lang import COMMAND_DENIED_NOT_AUTHORIZED


def settings_choose_campus(ctx: CallbackContext, id: int) -> None:
    kbd = [
        [
            InlineKeyboardButton(get_campus_name(CALLBACK_CAMPUS_KAZAN), callback_data=CALLBACK_CHOOSE_KAZAN),
            InlineKeyboardButton(get_campus_name(CALLBACK_CAMPUS_MOSCOW), callback_data=CALLBACK_CHOOSE_MOSCOW),
        ]
    ]

    ctx.bot.send_message(
        id,
        text='Если встреча будет оффлайн, то в каком кампусе?',
        reply_markup=InlineKeyboardMarkup(kbd)
    )


def settings_choose_online(ctx: CallbackContext, id: int) -> None:
    kbd = [
        [
            InlineKeyboardButton(get_online_status(CALLBACK_ONLINE_YES), callback_data=CALLBACK_CHOOSE_ONLINE),
        ],
        [
            InlineKeyboardButton(get_online_status(CALLBACK_ONLINE_NO), callback_data=CALLBACK_CHOOSE_OFFLINE),
        ]
    ]

    ctx.bot.send_message(
        id,
        text='Готов ли ты к встречам онлайн?\n\n'
             'Если ты готов к онлайну, то учти, что тебе может попасться пир из твоего кампуса, '
             'который выбрал исключительно оффлайн, если он был последним нечетным пиром из этой группы. '
             'В остальных случах тебе будут выбираться пиры случайным образом – '
             'как из твоего кампуса, так и из других.\n\n'
             'Если ты не готов к онлайну и хочешь только оффлайн, '
             'то тебе будет матчить только таких же неготовых в онлайну пиров из твоего кампуса. '
             'Исключение – когда ты остался последним нечетным пиром из своей группы. '
             'В таком случае система попытается найти тебе пира твоего кампуса, что выбирал как онлайн, так и оффлайн.',
        reply_markup=InlineKeyboardMarkup(kbd)
    )


def settings_choose_active(ctx: CallbackContext, id: int) -> None:
    kbd = [
        [
            InlineKeyboardButton(get_active_status(CALLBACK_ACTIVE_YES), callback_data=CALLBACK_CHOOSE_ACTIVE),
        ],
        [
            InlineKeyboardButton(get_active_status(CALLBACK_ACTIVE_NO), callback_data=CALLBACK_CHOOSE_INACTIVE),
        ]
    ]

    ctx.bot.send_message(
        id,
        text='На этой неделе участвуешь в случайном кофе?',
        reply_markup=InlineKeyboardMarkup(kbd)
    )


def settings_finish(ctx: CallbackContext, id: int) -> None:
    ctx.bot.send_message(
        id,
        text='Я запомнил твои предпочтения!\n\nУчти, что они автоматически продляются на все последующие недели, '
             'если ты их не изменишь.'
    )


def handler_command_settings(upd: Update, ctx: CallbackContext) -> None:
    if not ctx.user_data.get(USER_DATA_V1_AUTHORIZED, False):
        ctx.bot.send_message(upd.effective_user.id, text=COMMAND_DENIED_NOT_AUTHORIZED)
        return

    settings_choose_campus(ctx, upd.effective_user.id)

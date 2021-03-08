from typing import List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, PicklePersistence

from utils.callbackFormatter import create_callback_data

MODULE_START = 'start'
STATUS_CALLED = 'called'


def handler_command_start(update: Update, context: CallbackContext, persistence: PicklePersistence) -> None:
    greeting = "Привет!\n\nЭто бот неофициального RandomCoffee Школы 21.\n\nДля начала давай познакомимся поближе – " \
               "пройди аутентификацию через Intra OAuth."

    kbd = [
        [
            InlineKeyboardButton(
                "Аутентификация",
                url='',
                callback_data=create_callback_data(MODULE_START, STATUS_CALLED)
            ),
        ]
    ]

    context.bot.send_message(chat_id=update.effective_chat.id, text=greeting, reply_markup=InlineKeyboardMarkup(kbd))

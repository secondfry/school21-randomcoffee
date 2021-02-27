#!/usr/bin/env python

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv
import sqlite3
import logging

load_dotenv()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

GREETING = "Привет!\n\nЭто бот неофициального RandomCoffee Школы 21.\n\nДля начала давай познакомимся поближе – пройди аутентификацию через Intra OAuth."

    # kbd = [
    #     InlineKeyboardButton("Москва", callback_data='campus-msk'),
    #     InlineKeyboardButton("Казань", callback_data='campus-kzn'),
    # ]

def start(update: Update, context: CallbackContext) -> None:
    global GREETING

    kbd = [
        InlineKeyboardButton("Аутентификация", url=''),
    ]

    context.bot.send_message(chat_id=update.effective_chat.id, text=GREETING, reply_markup=InlineKeyboardMarkup(kbd))

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.edit_message_text(text=f"Selected option: {query.data}")

updater = Updater(TOKEN)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()
updater.idle()

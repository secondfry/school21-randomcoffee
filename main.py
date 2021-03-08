#!/usr/bin/env python

import logging
from typing import List

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, PicklePersistence

from config.env import TELEGRAM_TOKEN
from handlers.callback import handler_callback
from handlers.commandInfo import handler_command_info
from handlers.commandStart import handler_command_start
from handlers.error import handler_error
from utils.oauthClient import get_token_user_queue, GetTokenRequest

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def main():
    persistence = PicklePersistence(filename='store.pickle')
    updater = Updater(TELEGRAM_TOKEN, persistence=persistence, use_context=True)
    queue_data: List[GetTokenRequest] = []
    updater.job_queue.run_repeating(get_token_user_queue, interval=0.5, context={
        'queue_data': queue_data,
        'persistence': persistence
    })
    updater.dispatcher.add_handler(
        CommandHandler('start', lambda upd, ctx: handler_command_start(upd, ctx, persistence, queue_data))
    )
    updater.dispatcher.add_handler(CommandHandler('info', handler_command_info))
    updater.dispatcher.add_handler(CallbackQueryHandler(handler_callback))
    updater.dispatcher.add_error_handler(handler_error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

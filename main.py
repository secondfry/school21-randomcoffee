#!/usr/bin/env python

import logging
from datetime import timedelta, datetime
from typing import List

from pytz import timezone
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, PicklePersistence

from config.constants import TUESDAY
from config.env import TELEGRAM_TOKEN
from handlers.callback import handler_callback
from handlers.commandForceMatch import handler_command_forcematch
from handlers.commandInfo import handler_command_info
from handlers.commandSettings import handler_command_settings
from handlers.commandStart import handler_command_start
from handlers.error import handler_error
from utils.oauthClient import get_token_user_queue, GetTokenRequest
from utils.performMatch import perform_match

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def main():
    # Add persistence
    persistence = PicklePersistence(filename='store.pickle')

    # Create Updater
    updater = Updater(TELEGRAM_TOKEN, persistence=persistence, use_context=True)

    # Initialize queue data and start fetching Intra each 0.5s
    queue_data: List[GetTokenRequest] = []
    updater.job_queue.run_repeating(get_token_user_queue, interval=0.5, context=queue_data)

    # Initialize matcher
    moment = datetime.now(timezone('Europe/Moscow')).replace(hour=10, minute=0, second=0)
    moment += timedelta(days=(TUESDAY - moment.weekday()) % 7)
    updater.job_queue.run_repeating(
        perform_match,
        interval=timedelta(days=7),
        first=moment
    )

    # Handlers
    updater.dispatcher.add_handler(
        CommandHandler('start', lambda upd, ctx: handler_command_start(upd, ctx, queue_data))
    )
    updater.dispatcher.add_handler(CommandHandler('info', handler_command_info))
    updater.dispatcher.add_handler(CommandHandler('settings', handler_command_settings))
    updater.dispatcher.add_handler(CommandHandler('forcematch', handler_command_forcematch))
    updater.dispatcher.add_handler(CallbackQueryHandler(handler_callback))
    updater.dispatcher.add_error_handler(handler_error)

    # Go!
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

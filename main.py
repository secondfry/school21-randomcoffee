#!/usr/bin/env python

import logging
from datetime import datetime, timedelta

from pytz import timezone
from telegram import ext as telegram_ext

from config.constants import WEEKDAY_TUESDAY, WEEKDAY_WEDNESDAY
from config.env import TELEGRAM_TOKEN
from handlers.callback import handler_callback
from handlers.commandDump import handler_command_dump
from handlers.commandForceActive import handler_command_forceactive
from handlers.commandForceMatch import handler_command_forcematch
from handlers.commandForceNotify import handler_command_forcenotify
from handlers.commandForceRematch import handler_command_forcerematch
from handlers.commandInfo import handler_command_info
from handlers.commandSettings import handler_command_settings
from handlers.commandStart import handler_command_start
from handlers.commandStop import handler_command_stop
from handlers.error import handler_error
from utils.migrate import migrate
from utils.performMatch import perform_match
from utils.performRematch import perform_rematch

logging.basicConfig(
    format="[%(asctime)s][%(name)s][%(levelname)s] %(message)s", level=logging.INFO
)


def main():
    persistence = telegram_ext.PicklePersistence(filepath="store.pickle")
    job_queue = telegram_ext.JobQueue()

    # Initialize matcher
    moment = datetime.now(timezone("Europe/Moscow")).replace(
        hour=10, minute=0, second=0
    )
    moment += timedelta(days=(WEEKDAY_TUESDAY - moment.weekday()) % 7)
    job_queue.run_repeating(perform_match, interval=timedelta(days=7), first=moment)

    # Initialize re-matcher
    moment = datetime.now(timezone("Europe/Moscow")).replace(
        hour=10, minute=0, second=0
    )
    moment += timedelta(days=(WEEKDAY_WEDNESDAY - moment.weekday()) % 7)
    job_queue.run_repeating(perform_rematch, interval=timedelta(days=7), first=moment)

    app = (
        telegram_ext.ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .persistence(persistence)
        .job_queue(job_queue)
        .build()
    )

    # FIXME(secondfry):
    # migrate(app.user_data)

    # Handlers
    app.add_handler(telegram_ext.CommandHandler("start", handler_command_start))
    app.add_handler(telegram_ext.CommandHandler("info", handler_command_info))
    app.add_handler(telegram_ext.CommandHandler("settings", handler_command_settings))
    app.add_handler(telegram_ext.CommandHandler("stop", handler_command_stop))
    app.add_handler(
        telegram_ext.CommandHandler("forceactive", handler_command_forceactive)
    )
    app.add_handler(
        telegram_ext.CommandHandler("forcematch", handler_command_forcematch)
    )
    app.add_handler(
        telegram_ext.CommandHandler("forcerematch", handler_command_forcerematch)
    )
    app.add_handler(
        telegram_ext.CommandHandler("forcenotify", handler_command_forcenotify)
    )
    app.add_handler(telegram_ext.CommandHandler("dump", handler_command_dump))
    app.add_handler(telegram_ext.CallbackQueryHandler(handler_callback))
    app.add_error_handler(handler_error)

    # Go!
    app.run_polling()


if __name__ == "__main__":
    main()

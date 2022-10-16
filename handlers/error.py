import logging
import os
import pprint
import sys
from types import TracebackType
from typing import Optional, Union
import traceback

import telegram
import yaml
from config.constants import KEY_AUTHORIZED, KEY_TELEGRAM_USERNAME, KEY_USER_ID
from config.env import ADMIN_IDS
from telegram import constants as telegram_constants
from telegram import error as telegram_error
from telegram import ext as telegram_ext
from telegram import helpers as telegram_helpers


async def handle_common_block_errors(
    ctx: telegram_ext.CallbackContext, uid: int, ex: telegram_error.TelegramError
):
    if str(ex) not in [
        "Forbidden: bot was blocked by the user",
        "Forbidden: user is deactivated",
    ]:
        return False

    udata = ctx.application.user_data[uid]

    try:
        await ctx.bot.send_message(
            ADMIN_IDS[0],
            text="`[t#{0:<10}] {2:<8}` @{1} <= removed due to exception {3}".format(
                uid,
                udata.get(KEY_TELEGRAM_USERNAME, "???").replace("_", "\\_"),
                udata[KEY_USER_ID],
                str(ex),
            ),
            parse_mode=telegram_constants.ParseMode.MARKDOWN,
        )
    except Exception as e:
        logging.error("Could not send error report!")
        logging.exception(e)

    udata.clear()
    udata[KEY_AUTHORIZED] = False
    return True


def format_traceback(tb: Union[TracebackType, None]) -> str:
    if not tb:
        return "<traceback unavailable>"

    ret = []
    skipped = 0
    for line in traceback.format_tb(tb):
        if line.find("site-packages") != -1:
            skipped += 1
            continue

        if skipped:
            ret.append(f'{" " * 8}... x{skipped}\n')
            skipped = 0

        line = line.replace(os.getcwd(), "...")
        ret.append(line)

    if skipped:
        ret.append(f'{" " * 8}... x{skipped}')

    return "".join(ret)


def format_exception() -> str:
    ex_type, ex, tb = sys.exc_info()
    formatted_ex = f"Exception:\n```\n{format_traceback(tb)}\n````{ex_type.__module__}.{ex_type.__name__}: {ex}`"
    return formatted_ex


async def send_error(
    ctx: telegram_ext.CallbackContext,
    uid: Union[int, None],
    message: Optional[str],
    ex: Exception,
    should_escape: bool = True,
):
    udata = ctx.application.user_data.get(uid, {})
    telegram_username = udata.get(KEY_TELEGRAM_USERNAME, "???")
    intra_login = udata.get(KEY_USER_ID, "???")

    if not message:
        message = "Unspecified error."
    if should_escape:
        message = telegram_helpers.escape_markdown(message, version=2)

    formatted_ex = telegram_helpers.escape_markdown(ex.__str__(), version=2)
    try:
        formatted_ex = format_exception()
    except Exception:
        pass

    try:
        await ctx.bot.send_message(
            ADMIN_IDS[0],
            text=f"`[tid#{uid}]``[tus#{telegram_username}]` `{intra_login}` Error\!\n{message}\n{formatted_ex}",
            parse_mode=telegram_constants.ParseMode.MARKDOWN_V2,
        )
    except Exception as e:
        logging.error("Could not send error report!")
        logging.exception(e)


async def handler_error(
    upd: Optional[telegram.Update], ctx: telegram_ext.CallbackContext
):
    formatted_upd = upd.__str__()
    try:
        formatted_upd = pprint.pformat(yaml.safe_load(formatted_upd))
    except Exception:
        pass

    await send_error(
        ctx,
        upd.effective_user.id if upd and upd.effective_user else None,
        "Root update:\n```\n{}\n```".format(formatted_upd),
        ctx.error,
        should_escape=False,
    )
    logging.error("telegram.Update caused exception! [%s]", upd)
    logging.exception(ctx.error)

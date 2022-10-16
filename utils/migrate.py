import json
import os
from typing import Dict

from config.constants import (
    KEY_TELEGRAM_ID,
    KEY_VERSION,
)
from typings import TokenUser
from telegram import ext as telegram_ext

from utils.getters import get_primary_campus


def get_campus_from_data_cache(intra_login: str) -> str:
    dirpath = os.path.join("data", intra_login)
    if not os.path.isdir(dirpath):
        return "???"

    files = os.listdir(dirpath)
    files.sort(reverse=True)
    filepath = os.path.join(dirpath, files[0])

    with open(filepath, "r+") as f:
        data: TokenUser = json.load(f)

    campus = get_primary_campus(data)
    return campus if campus else "???"


def migrate_from_2_to_3(data: Dict, uid: int):
    data[KEY_VERSION] = 3

    if KEY_TELEGRAM_ID not in data:
        data[KEY_TELEGRAM_ID] = uid


async def migrate(ctx: telegram_ext.CallbackContext) -> None:
    user_data = ctx.application.user_data
    for uid, data in user_data.items():
        if data.get(KEY_VERSION, 0) < 3:
            migrate_from_2_to_3(data, uid)

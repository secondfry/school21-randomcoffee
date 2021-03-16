import json
import os
from typing import Dict

from telegram.ext import PicklePersistence

from config.constants import (
    USER_DATA_VERSION,
    USER_DATA_V1_AUTHORIZED,
    USER_DATA_V1_INTRA_LOGIN,
    USER_DATA_V1_INTRA_CAMPUS,
    USER_DATA_TOKEN_SUCCESS,
    USER_DATA_V1_INTRA_TOKEN,
    USER_DATA_V1_TELEGRAM_USERNAME,
    USER_DATA_CAMPUS,
    USER_DATA_V1_SETTINGS_CAMPUS,
    USER_DATA_ONLINE,
    USER_DATA_V1_SETTINGS_ONLINE,
    USER_DATA_ACTIVE,
    USER_DATA_V1_SETTINGS_ACTIVE,
    USER_DATA_LOGIN,
    USER_DATA_TELEGRAM_USERNAME,
    USER_DATA_V1_MATCH_ACCEPTED,
    USER_DATA_ACCEPTED,
    USER_DATA_MATCHED_WITH,
    USER_DATA_V1_MATCH_WITH,
)
from typings import TokenUser
from utils.getters import get_primary_campus


def get_campus_from_data_cache(intra_login: str) -> str:
    dirpath = os.path.join('data', intra_login)
    if not os.path.isdir(dirpath):
        return '???'

    files = os.listdir(dirpath)
    files.sort(reverse=True)
    filepath = os.path.join(dirpath, files[0])

    with open(filepath, 'r+') as f:
        data: TokenUser = json.load(f)

    campus = get_primary_campus(data)
    return campus if campus else '???'


def migrate_from_0_to_1(data: Dict):
    data[USER_DATA_VERSION] = 1

    if USER_DATA_LOGIN in data:
        intra_login = data[USER_DATA_LOGIN]
        data[USER_DATA_V1_AUTHORIZED] = True
        data[USER_DATA_V1_INTRA_LOGIN] = intra_login
        data[USER_DATA_V1_INTRA_CAMPUS] = get_campus_from_data_cache(intra_login)

    if USER_DATA_TOKEN_SUCCESS in data:
        data[USER_DATA_V1_INTRA_TOKEN] = data[USER_DATA_TOKEN_SUCCESS]

    if USER_DATA_TELEGRAM_USERNAME in data:
        username = data[USER_DATA_TELEGRAM_USERNAME]
        if username:
            data[USER_DATA_V1_TELEGRAM_USERNAME] = username
        else:
            data[USER_DATA_V1_TELEGRAM_USERNAME] = '???'
    else:
        data[USER_DATA_V1_TELEGRAM_USERNAME] = '???'

    if USER_DATA_CAMPUS in data:
        data[USER_DATA_V1_SETTINGS_CAMPUS] = data[USER_DATA_CAMPUS]

    if USER_DATA_ONLINE in data:
        data[USER_DATA_V1_SETTINGS_ONLINE] = data[USER_DATA_ONLINE]

    if USER_DATA_ACTIVE in data:
        data[USER_DATA_V1_SETTINGS_ACTIVE] = data[USER_DATA_ACTIVE]

    if USER_DATA_ACCEPTED in data:
        data[USER_DATA_V1_MATCH_ACCEPTED] = data[USER_DATA_ACCEPTED]

    if USER_DATA_MATCHED_WITH in data:
        data[USER_DATA_V1_MATCH_WITH] = data[USER_DATA_MATCHED_WITH]


def migrate(user_data: Dict[int, Dict[object, object]]) -> None:
    for uid, data in user_data.items():
        if data.get(USER_DATA_VERSION, 0) < 1:
            migrate_from_0_to_1(data)

from typing import Optional, Dict, Any

from config.constants import (
    CALLBACK_CAMPUS_KAZAN,
    CALLBACK_CAMPUS_MOSCOW,
    CALLBACK_ONLINE_NO,
    CALLBACK_ONLINE_YES,
    CALLBACK_ACTIVE_YES,
    CALLBACK_ACTIVE_NO,
    USER_DATA_V1_SETTINGS_ONLINE,
    USER_DATA_V1_SETTINGS_CAMPUS,
    USER_DATA_V1_INTRA_CAMPUS,
    USER_DATA_V1_MATCH_ACCEPTED,
)
from typings import TokenUser


def get_campus_name(slug: str) -> str:
    return {
        CALLBACK_CAMPUS_KAZAN: 'Казань',
        CALLBACK_CAMPUS_MOSCOW: 'Москва'
    }.get(slug, '???')


def get_online_status(slug: str) -> str:
    return {
        CALLBACK_ONLINE_YES: 'Готов как к онлайну, так и к оффлайну',
        CALLBACK_ONLINE_NO: 'Хочу только оффлайн',
    }.get(slug, '???')


def get_active_status(slug: str) -> str:
    return {
        CALLBACK_ACTIVE_YES: 'Да, все в силе',
        CALLBACK_ACTIVE_NO: 'Пока что не хочу случайного кофе',
    }.get(slug, '???')


def get_accepted() -> str:
    return 'Подтверджено'


def get_accepted_sign(data: Dict[str, Any]) -> str:
    return {
        True: '+',
        False: '-'
    }.get(data[USER_DATA_V1_MATCH_ACCEPTED], '?')


def get_primary_campus(data: TokenUser) -> Optional[str]:
    if not data['campus']:
        return None

    id: Optional[int] = None

    for campus_user in data['campus_users']:
        if campus_user['is_primary']:
            id = campus_user['campus_id']

    if not id:
        return None

    for campus in data['campus']:
        if campus['id'] == id:
            return campus['name'].lower()

    return None


def get_bucket(data: Dict[str, Any]):
    online = data.get(USER_DATA_V1_SETTINGS_ONLINE, 'unset')
    if online == CALLBACK_ONLINE_YES:
        return 'online'

    campus = data.get(USER_DATA_V1_SETTINGS_CAMPUS, 'unset')

    if campus == 'unset':
        campus = data.get(USER_DATA_V1_INTRA_CAMPUS, 'unset')

    return campus

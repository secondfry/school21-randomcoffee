from config.constants import CALLBACK_CAMPUS_KAZAN, CALLBACK_CAMPUS_MOSCOW, CALLBACK_ONLINE_NO, CALLBACK_ONLINE_YES


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

import re

TOKEN_REGEXP = re.compile('[0-9a-f]{64}')
USER_DATA_TOKEN_SUCCESS = 'intra_token_success'
USER_DATA_LOGIN = 'intra_login'
USER_DATA_TELEGRAM_USERNAME = 'telegram_username'

CALLBACK_ACTION_SETTING = 'settings'

CALLBACK_STEP_CAMPUS = 'campus'
USER_DATA_CAMPUS = 'campus'
CALLBACK_CAMPUS_KAZAN = 'kazan'
CALLBACK_CAMPUS_MOSCOW = 'moscow'
CALLBACK_CHOOSE_KAZAN = '-'.join([CALLBACK_ACTION_SETTING, CALLBACK_STEP_CAMPUS, CALLBACK_CAMPUS_KAZAN])
CALLBACK_CHOOSE_MOSCOW = '-'.join([CALLBACK_ACTION_SETTING, CALLBACK_STEP_CAMPUS, CALLBACK_CAMPUS_MOSCOW])

CALLBACK_STEP_ONLINE = 'online'
USER_DATA_ONLINE = 'online'
CALLBACK_ONLINE_YES = 'yes'
CALLBACK_ONLINE_NO = 'no'
CALLBACK_CHOOSE_ONLINE = '-'.join([CALLBACK_ACTION_SETTING, CALLBACK_STEP_ONLINE, CALLBACK_ONLINE_YES])
CALLBACK_CHOOSE_OFFLINE = '-'.join([CALLBACK_ACTION_SETTING, CALLBACK_STEP_ONLINE, CALLBACK_ONLINE_NO])

CALLBACK_ACTION_MATCH = 'match'
CALLBACK_STEP_ACCEPT = 'accept'
USER_DATA_ACCEPTED = 'accepted'

USER_DATA_MATCHED_WITH = 'matched_with'

TUESDAY = 1

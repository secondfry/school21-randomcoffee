import os
from datetime import datetime
from typing import TypedDict, Union, List, Any, Optional

import requests
from telegram.ext import CallbackContext, PicklePersistence

from config.constants import USER_DATA_LOGIN
from config.env import INTRA_CLIENT_ID, INTRA_CLIENT_SECRET, INTRA_REDIRECT_URI
from utils.json_write import json_write


class TokenSuccess(TypedDict):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str
    created_at: int


def check_access_code(code: str) -> Optional[TokenSuccess]:
    res = requests.post('https://api.intra.42.fr/oauth/token', data={
        'grant_type': 'authorization_code',
        'client_id': INTRA_CLIENT_ID,
        'client_secret': INTRA_CLIENT_SECRET,
        'redirect_uri': INTRA_REDIRECT_URI,
        'code': code
    })

    if res.status_code == 200:
        return res.json()

    return None


class Skill(TypedDict):
    id: int
    name: str
    level: int


class User(TypedDict):
    id: int
    login: str
    url: str


class Cursus(TypedDict):
    id: int
    created_at: str
    name: str
    slug: str


class CursusUser(TypedDict):
    grade: str
    level: int
    skills: List[Skill]
    blackholed_at: Union[str, None]
    id: int
    begin_at: str
    end_at: Union[str, None]
    cursus_id: int
    has_coalition: bool
    user: User
    cursus: Cursus


class Project(TypedDict):
    id: int
    name: str
    slug: str
    parent_id: Union[int, None]


class ProjectUser(TypedDict):
    id: int
    occurrence: int
    final_mark: int
    status: str
    # 'validated?': bool
    current_team_id: int
    project: Project
    cursus_ids: List[int]
    marked_at: str
    marked: bool
    retriable_at: str


class LanguageUser(TypedDict):
    id: int
    language_id: int
    user_id: int
    position: int
    created_at: str


class Achievement(TypedDict):
    id: int
    name: str
    description: str
    tier: str
    kind: str
    visible: bool
    image: str
    nbr_of_success: Union[int, None]
    users_url: str


class ExpertiseUser(TypedDict):
    id: int
    expertise_id: int
    interested: bool
    value: int
    contact_me: bool
    created_at: str
    user_id: int


class Language(TypedDict):
    id: int
    name: str
    identifier: str
    created_at: str
    updated_at: str


class Campus(TypedDict):
    id: int
    name: str
    time_zone: str
    language: Language
    users_count: int
    vogsphere_id: int
    country: str
    address: str
    zip: str
    city: str
    website: str
    facebook: str
    twitter: str
    active: bool
    email_extension: str


class CampusUser(TypedDict):
    id: int
    user_id: int
    campus_id: int
    is_primary: bool


class TokenUser(TypedDict):
    id: int
    email: str
    login: int
    first_name: str
    last_name: str
    usual_first_name: Union[str, None]
    url: str
    phone: str
    displayname: str
    usual_full_name: str
    image_url: str
    # 'staff?': bool
    correction_point: int
    pool_month: str
    pool_year: str
    location: Union[str, None]
    wallet: int
    anonymize_date: str
    groups: List[Any]
    cursus_users: List[CursusUser]
    projects_users: List[ProjectUser]
    languages_users: List[LanguageUser]
    achievements: List[Achievement]
    titles: List[Any]
    titles_users: List[Any]
    partnerships: List[Any]
    patroned: List[Any]
    patroning: List[Any]
    expertises_users: List[ExpertiseUser]
    roles: List[Any]
    campus: List[Campus]
    campus_users: List[CampusUser]


def get_token_user(token: str) -> Optional[TokenUser]:
    res = requests.get('https://api.intra.42.fr/v2/me?access_token={}'.format(token))

    if res.status_code == 200:
        data: TokenUser = res.json()

        folder = 'data/{}'.format(data['login'])
        if not os.path.isdir(folder):
            os.mkdir(folder)

        timestamp = datetime.now().isoformat()
        json_write(data, '{}/{}-data.json'.format(folder, timestamp))

        return data

    return None


class GetTokenRequest(TypedDict):
    id: int
    token: TokenSuccess


class GetTokenUserQueueContext(TypedDict):
    queue_data: List[GetTokenRequest]
    persistence: PicklePersistence


def get_token_user_queue(ctx: CallbackContext) -> None:
    context: GetTokenUserQueueContext = ctx.job.context
    queue = context['queue_data']
    persistence = context['persistence']

    if not queue:
        return

    request = queue.pop()
    token = request['token']

    if token['created_at'] + token['expires_in'] < datetime.utcnow().timestamp():
        ctx.bot.send_message(request['id'], text='Пока мы ожидали ответ Интры мой токен доступа успел протухнуть :('
                                                 '\n\nПовтори авторизацию, пожалуйста!')
        return

    token_user = get_token_user(token['access_token'])
    persistence.user_data.get(request['id'])[USER_DATA_LOGIN] = token_user['login']
    ctx.bot.send_message(request['id'], text='Привет, {}'.format(token_user['login']))

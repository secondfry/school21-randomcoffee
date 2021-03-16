import os
from datetime import datetime
from typing import List, Optional

import requests
from telegram.ext import CallbackContext

from config.constants import (
    USER_DATA_V1_AUTHORIZED, USER_DATA_V1_INTRA_LOGIN,
    USER_DATA_V1_INTRA_CAMPUS,
)
from config.env import INTRA_CLIENT_ID, INTRA_CLIENT_SECRET, INTRA_REDIRECT_URI
from handlers.commandSettings import settings_choose_campus
from typings import Token, TokenUser, GetTokenRequest
from utils.getters import get_primary_campus
from utils.json_write import json_write


def check_access_code(code: str) -> Optional[Token]:
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


def get_token_user_queue(ctx: CallbackContext) -> None:
    queue: List[GetTokenRequest] = ctx.job.context

    if not queue:
        return

    request = queue.pop()
    uid = request['id']
    token = request['token']

    if token['created_at'] + token['expires_in'] < datetime.utcnow().timestamp():
        try:
            ctx.bot.send_message(uid, text='Пока мы ожидали ответ Интры мой токен доступа успел протухнуть :(\n\n'
                                           'Повтори авторизацию, пожалуйста!')
        except:
            # TODO actually handle exception
            pass
        return

    token_user = get_token_user(token['access_token'])
    ctx.dispatcher.user_data[uid][USER_DATA_V1_AUTHORIZED] = True
    ctx.dispatcher.user_data[uid][USER_DATA_V1_INTRA_LOGIN] = token_user['login']
    ctx.dispatcher.user_data[uid][USER_DATA_V1_INTRA_CAMPUS] = get_primary_campus(token_user)

    try:
        ctx.bot.send_message(
            request['id'],
            text='Привет, {}'.format(token_user['login'])
        )
    except:
        # TODO actually handle exception
        pass

    settings_choose_campus(ctx, request['id'])

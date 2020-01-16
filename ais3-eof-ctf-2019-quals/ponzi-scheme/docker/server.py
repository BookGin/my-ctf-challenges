#!/usr/bin/env python3
import hashlib, uuid, hmac, datetime
from functools import wraps
from asyncio import sleep
from secrets import token_urlsafe

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER
from starlette.background import BackgroundTask


import config
from database import Database
import powser

'''
helpers
'''
def login_required(func):
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        if (user := await db.get_user(request.path_params['uid'])) is None:
            return RedirectResponse(url=app.url_path_for('index'), status_code=HTTP_303_SEE_OTHER)
        return await func(request, user, *args, **kwargs)
    return wrapper

def DelayTransferTask(sleep_sec, *args):
    return BackgroundTask(_delay_transfer, sleep_sec, *args)

async def _delay_transfer(sleep_sec, *args):
    await sleep(sleep_sec)
    await db.transfer(*args)

'''
views
'''
async def index(request):
    ip = request.headers.get('X-Real-IP', '127.0.0.1')
    if (answer := request.query_params.get('answer')) is None:
        prefix, time_remain = powser.get_challenge(ip)
        return HTMLResponse(config.pow_html.render(dict(
            prefix=prefix,
            difficulty=powser.difficulty,
            ip=ip,
            time_remain=time_remain,
            min_refresh_time=powser.min_refresh_time,
        )))
    res, msg = powser.verify_client(ip, str(answer), with_msg=True)
    if not res:
        return HTMLResponse(msg)
    user = await db.create_user(token_urlsafe(16), config.user_init_balance)
    return RedirectResponse(url='/' + user.uid, status_code=HTTP_303_SEE_OTHER)


@login_required
async def home(request, user):
    if user.balance >= 10000:
        msg = config.flag
    elif bool(user.bankrupt):
        msg = 'You are bankrupt ¯\_(ツ)_/¯'
    else:
        msg = "Once you have &gt;= $10,000, you'll see the flag in this page."
    task = None
    if request.method == 'POST':
        if user.balance <= 0:
            return HTMLResponse('Not enough balance')
        form = await request.form()
        if form.get('csrf') != user.csrf:
            return HTMLResponse("Invalid CSRF token")
        if not (0 <= (n := int(form.get('plan', -1))) <= 2):
            return HTMLResponse("Ooopsie, we don't have this plan")
        # update csrf token
        await db.update_user_csrf(user.uid)
        # deduce user's balance first
        if not await db.transfer(user.uid, config.ponzi_uid, user.balance):
            return HTMLResponse('Not enough balance')
        sleep_sec, reward = config.plans['term'][n], int(config.plans['_rate'][n] * user.balance)
        msg = f"Thank you for investing Ponzi! You'll get back $ {reward} in {sleep_sec} seconds."
        task = DelayTransferTask(sleep_sec, config.ponzi_uid, user.uid, reward)
        user = await db.get_user(user.uid)
    user_bk, ponzi_max, user_count, ponzi_b  = await db.get_stats()
    return HTMLResponse(config.home_html.render(dict(user=user, plans=config.plans, msg=msg, stats={
        "Ponzi's current balance": ponzi_b,
        "Ponzi's highest balance": ponzi_max,
        "Number of investers": user_count - 1, # ponzi,
        "Number of bankrupt investers": user_bk
    })),background=task)

'''
globals
'''
async def setup():
    await db.connect()
    await db.init_user_table()
    await db.create_user(config.ponzi_uid, config.ponzi_init_balance)
    await db.init_stat_table()
    await db.create_stat()

db = Database('sqlite:///' + config.db_path)
powser = powser.Powser(
    db_path=config.powser_path,
    difficulty=config.powser_diffculty,
    min_refresh_time=config.powser_min_refresh_time,
    default_expired_time=config.powser_default_expired_time
)

app = Starlette(
    debug=config.debug,
    routes=[
        Route('/', endpoint=index, methods=['GET'], name='index'),
        Route('/{uid:str}', endpoint=home, methods=['GET', 'POST'], name='home'),
    ],
    on_startup=[setup],
    on_shutdown=[db.disconnect]
)

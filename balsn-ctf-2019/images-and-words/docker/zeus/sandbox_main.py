#!/usr/bin/env python3
from pathlib import Path
import secrets
import asyncio
import subprocess

from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.background import BackgroundTask

import config
import powser

server = Starlette(debug=config.debug)
powser = powser.Powser(db_path='./pow/pow.sqlite3', difficulty=config.difficulty)

async def remove_sandbox(sandbox_name):
    await asyncio.sleep(config.recycle_t)
    subprocess.run(['sudo', '/usr/bin/remove_sandbox.sh', sandbox_name])

def create_sandbox(sandbox_name):
    subprocess.run(['sudo', '/usr/bin/create_sandbox.sh', sandbox_name])

@server.route('/')
async def index(request):
    ip = request.headers['X-Real-IP']
    answer = request.query_params.get('answer')
    if answer is None:
        prefix, time_remain = powser.get_challenge(ip)
        return HTMLResponse(f'''
{prefix} {powser.difficulty}

sha256({prefix} + ???) == {'0'*powser.difficulty}({powser.difficulty})...

<form method="GET" action="/">
  <input type="text" name="answer">
  <input type="submit" value="Submit">
</form>

We will create an isolated sandbox for challengers to prevent you from being interfered by others.

IP: {ip}
Time remain: {time_remain} seonds
You need to await {time_remain - powser.min_refresh_time} seconds to get a new challenge.
'''.replace('\n', '<br>\n'))
    res, msg = powser.verify_client(ip, str(answer), with_msg=True)
    if not res:
        return HTMLResponse(msg)
    sandbox_name = secrets.token_urlsafe(32)[:32].replace('-', '_') # useradd will parse '-nabc' ... -_-
    create_sandbox(sandbox_name)
    return HTMLResponse(f'''
Your sandbox is available in <a href="/{sandbox_name}/">/{sandbox_name}/</a><br>
It's will be automatically deleted after {config.recycle_t} seconds.
''', background=BackgroundTask(remove_sandbox, sandbox_name))

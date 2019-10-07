#!/usr/bin/env python3
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from redis import Redis
from rq import Queue

import config
from powser import Powser
import chrome_headless

app = Starlette(debug=config.debug)
queue = None
powser = None

@app.on_event('startup')
def init():
    global queue, powser
    queue = Queue(connection=Redis(unix_socket_path='/var/run/redis/redis-server.sock'))
    powser = Powser(db_path='./pow/pow.sqlite3', difficulty=config.difficulty)

@app.route('/')
async def index(request):
    ip = request.headers['X-Real-IP']
    answer = request.query_params.get('answer')
    url = request.query_params.get('url')
    if answer is None or url is None or not (url.startswith('http://') or url.startswith('https://')):
        prefix, time_remain = powser.get_challenge(ip)
        return HTMLResponse(f'''
{prefix} {powser.difficulty}

sha256({prefix} + ???) == {'0'*powser.difficulty}({powser.difficulty})...

<form method="GET" action="/">
  PoW answer: <input type="text" name="answer">
  URL to visit: <input type="text" name="url" placeholder="https://balsn.tw/">
  (url should start with http:// or https://)
  <input type="submit" value="Submit">
</form>

IP: {ip}
Time remain: {time_remain} seonds
You need to await {time_remain - powser.min_refresh_time} seconds to get a new challenge.
'''.replace('\n', '<br>\n'))
    res, msg = powser.verify_client(ip, str(answer), with_msg=True)
    if not res:
        return HTMLResponse(msg)
    queue.enqueue(chrome_headless.browse, url)
    return HTMLResponse('Okay, challenge accepted.')

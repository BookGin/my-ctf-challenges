#!/usr/bin/env python3
import hashlib, uuid, hmac, datetime, secrets, asyncio, os, subprocess, datetime
from pathlib import Path
from pwd import getpwnam
from starlette.background import BackgroundTasks
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
#from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

TemplateResponse = Jinja2Templates(directory='/app/templates').TemplateResponse
RATE_LIMIT_SEC = 10
root_dir = Path('/sandbox')

def err(r, msg):
    return TemplateResponse('error.html', {'request': r, 'msg': msg})

def setuid(uid):
    # https://stackoverflow.com/a/11062896/11712282
    os.setgid(getpwnam(uid).pw_gid)
    os.setuid(getpwnam(uid).pw_uid)

def run(uid, cmds, check=True, return_returncode=False):
    proc = subprocess.run(
        cmds,
        cwd=root_dir / uid,
        capture_output=True,
        preexec_fn=lambda: setuid(uid),
        timeout=10
    )
    if return_returncode:
        return proc.returncode
    if check and proc.returncode != 0:
        raise Exception(proc.stderr.decode(errors='backslashreplace'))
    return proc.stdout.decode(errors='backslashreplace')

async def index(r):
    if not r.session:
        ip = r.headers['x-real-ip']
        fi = (Path('/ips/') / ip)
        now = datetime.datetime.now().timestamp()
        if fi.is_file() and now - fi.stat().st_mtime < RATE_LIMIT_SEC:
            wait_time = RATE_LIMIT_SEC - (now - fi.stat().st_mtime)
            return err(r, f"{ip} rate-limit exceeded! Please wait for {wait_time} seconds!")
        fi.touch()

        r.session['q'] = []
        uid = secrets.token_hex(16)
        subprocess.check_call(['bash', '/app/create_sandbox.sh', uid])
        subprocess.check_call(['mkdir', str(root_dir / uid)], preexec_fn=lambda: setuid(uid))
        subprocess.check_call(['chmod', '700', str(root_dir / uid)], preexec_fn=lambda: setuid(uid))
        r.session['uid'] = uid

    args = r.query_params.get('args', '')
    files = [i[len('./'):] for i in run(r.session['uid'], ['find', '.']).splitlines()]
    if r.query_params.get('op') == 'show' and args:
        names = args.split(' ')
        if not all(name in files for name in names):
            return err(r, 'Only your own playlists can be shown!')
        songs = run(r.session['uid'], ['ls', '-A'] + names).splitlines()
    elif r.query_params.get('op') == 'stat':
        if not args:
            songs = run(r.session['uid'], ['du', '-sh', '.']).splitlines()
        else:
            names = args.split(' ')
            if not all(name in files for name in names):
                return err(r, 'Only your own playlists can be shown!')
            songs = run(r.session['uid'], ['du', '-sh'] + names).splitlines()
    elif r.query_params.get('op') == 'create':
        if '..' in args:
            return err(r, 'Illegal playlist name')
        args = args.split(' ')
        playlists = run(r.session['uid'], ['ls', '-A']).splitlines()
        if len(playlists) + len(args) > 2:
            return err(r, 'Regular user can only create at most 2 playlists!')
        run(r.session['uid'], ['mkdir'] + args)
        return RedirectResponse('/')
    else:
        songs = files

    return TemplateResponse('index.html', {
        'request': r,
        'queue': r.session['q'],
        'uid': r.session['uid'],
        'songs': songs
    })

async def qshuf(r):
    r.session['q'] = run(r.session['uid'], ['shuf', '-e'] + r.session['q']).splitlines()
    return RedirectResponse('/')

async def qskip(r):
    if r.session['q']:
        r.session['q'].pop(0)
    return RedirectResponse('/')

async def qadd(r):
    args = r.query_params.get('args', '')
    if '..' in args:
        return err(r, 'Illegal playlist or song name')
    args = args.split(' ')
    run(r.session['uid'], ['ls'] + ['../' + arg.replace(':', '/') if ':' in arg else arg for arg in args])
    r.session['q'] += args
    return RedirectResponse('/')

async def error_500(r, exc):
    return err(r, exc)

app = Starlette(
    debug=False,
    routes=[
        Route('/', endpoint=index, methods=['GET']),
        Route('/q/add', endpoint=qadd, methods=['GET']),
        Route('/q/skip', endpoint=qskip, methods=['GET']),
        Route('/q/shuf', endpoint=qshuf, methods=['GET']),
        #Mount('/static',  StaticFiles(directory='static'))
    ],
    middleware=[
        Middleware(SessionMiddleware, secret_key=Path('/root/key').read_bytes())
    ],
    exception_handlers={
        500: error_500
    }
)


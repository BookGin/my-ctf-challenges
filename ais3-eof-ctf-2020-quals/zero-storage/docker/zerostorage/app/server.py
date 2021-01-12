#!usr/bin/env python3
import hashlib, uuid, hmac, datetime, secrets, aiosqlite, asyncio, aiofiles, os, socket, sys
from urllib.parse import urlparse
from functools import wraps
from collections import namedtuple
from pathlib import Path

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse, FileResponse
from starlette.status import HTTP_303_SEE_OTHER
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.exceptions import HTTPException

from redis import Redis
from rq import Queue

TemplateResponse = Jinja2Templates(directory='templates').TemplateResponse
Redirect = lambda name: RedirectResponse(url=app.url_path_for(name), status_code=HTTP_303_SEE_OTHER)
rand = lambda: secrets.token_urlsafe(24)

queue = None
db = None

DATABASE_URL = os.getenv('DATABASE_URL') or "./db.sqlite3"
REDIS_HOST = os.getenv('REDIS_HOST') or 'localhost'
THIS_URL = os.getenv('THIS_URL') or 'http://localhost/'
THIS_HOST = urlparse(THIS_URL).netloc
FLAG_A = os.getenv('FLAG_A') or 'FLAG_A'
FLAG_B = os.getenv('FLAG_B') or 'FLAG_B'

ADMIN_HOST = os.getenv('ADMIN_HOST') or 'localhost'
ADMIN_IP = socket.gethostbyname(ADMIN_HOST)
ADMIN_FILENAME = os.getenv("ADMIN_FILENAME") or 'flag_a.txt'
SECRET_KEY = os.getenv("SECRET_KEY") or 'secret_key'
UPLOAD_DIR = Path('/tmp/files/')
UPLOAD_DIR.mkdir(exist_ok=True)

'''
Cache
'''

_id2name = {}
_name2id = {}

async def _update_name_id_dicts():
    async with db.execute('SELECT id, user FROM users') as cursor:
        rows = await cursor.fetchall()
    global _id2name
    global _name2id
    for user_id, name in rows:
        _id2name[user_id] = name
        _name2id[name] = user_id

async def get_name_from_id(_id):
    if _id in _id2name:
        return _id2name[_id]
    await _update_name_id_dicts()
    return _id2name.get(_id)

async def get_id_from_name(name):
    if name in _name2id:
        return _name2id[name]
    await _update_name_id_dicts()
    return _name2id.get(name)

'''
Helper functions
'''

async def is_friend(id0, id1):
    if id0 is None or id1 is None:
        return False
    if id0 == id1:
        return True
    async with db.execute('''
SELECT COUNT(*) FROM friendship WHERE (user_id = ? AND to_id = ?) OR (to_id = ? AND user_id = ?)
''', (id0, id1, id0, id1)) as cursor:
        num, = await cursor.fetchone()
    return num == 2

def is_admin_request(request):
    # Prevent from dns rebinding
    return request.headers.get('X-Real-IP') == ADMIN_IP and request.headers.get('host') == THIS_HOST

def login_required(func):
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        res = Redirect('index')
        if 'id' not in request.session:
            return res
        if request.session['id'] == 0 and not is_admin_request(request):
            return TemplateResponse('show.html', {'request': request, 'note': "Admin is not allowed to login with this IP."})
        async with db.execute('SELECT user FROM users WHERE id = ?', (request.session['id'], )) as cursor:
            row = await cursor.fetchone()
        name, = (None, ) if row is None else row
        if name is None:
            return res
        user = namedtuple('User', ['id', 'name', 'filenames'])(id=request.session['id'], name=name, filenames=request.session['filenames'])
        return await func(request, user, *args, **kwargs)
    return wrapper

async def startup():
    global db
    db = await aiosqlite.connect(DATABASE_URL)
    await db.executescript('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT UNIQUE NOT NULL,
    pass TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS friendship (
    user_id INTEGER NOT NULL,
    to_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(to_id) REFERENCES users(id),
    UNIQUE(user_id, to_id) ON CONFLICT ABORT
);

CREATE TABLE IF NOT EXISTS files (
    owner_id INTEGER NOT NULL,
    filename TEXT UNIQUE NOT NULL,
    FOREIGN KEY(owner_id) REFERENCES users(id)
);
''')
    await db.execute(
        'INSERT OR IGNORE INTO users (id, user, pass) VALUES (?, ?, ?)',
        (0, 'admin', FLAG_B)
    )
    await db.execute(
        'INSERT OR IGNORE INTO files (owner_id, filename) VALUES (?, ?)',
        (0, ADMIN_FILENAME)
    )
    await db.commit()

    try:
        # "x" mode has the O_EXCL flag :)
        # https://github.com/python/cpython/blob/63298930fb531ba2bb4f23bc3b915dbf1e17e9e1/Modules/_io/fileio.c#L294-L306
        with open(UPLOAD_DIR / ADMIN_FILENAME, "x") as f:
            f.write(FLAG_A)
    except FileExistsError:
        pass

    global queue
    queue = Queue(connection=Redis(REDIS_HOST))

async def shutdown():
    await db.close()

'''
Route
'''

async def index(request):
    return TemplateResponse('index.html', {'request': request})

async def login(request):
    form = await request.form()
    request.session.clear()
    user, pas = form.get('user', ''), form.get('pass', '')
    async with db.execute('SELECT id, pass FROM users WHERE user = ?', (user,)) as cursor:
        row = await cursor.fetchone()
    uid, correct_pas = (None, None) if row is None else row
    if uid is None: # no such user, so register a new account
        async with db.execute('INSERT INTO users (user, pass) VALUES (?, ?)', (user, pas)) as cursor:
            await db.commit()
        uid = cursor.lastrowid
    else: # user exists
        if not secrets.compare_digest(correct_pas, pas): # incorrect password
            return TemplateResponse('show.html', {'request': request, 'note': "Incorrect password!"})
    request.session.update({'id': uid, 'filenames': []})
    return Redirect('home')

async def admin_login(request):
    if is_admin_request(request):
        request.session.clear()
        request.session.update({'id': 0, 'filenames': [ADMIN_FILENAME]})
    return Redirect('home')

@login_required
async def home(request, user):
    async with db.execute('SELECT user_id, to_id FROM friendship WHERE user_id = ? OR to_id = ?', (user.id, user.id)) as cursor:
        rows = await cursor.fetchall()
    friendship = {} # from/to_id: from/to_id, status
    for from_id, to_id in rows:
        if from_id == user.id:
            friendship[to_id] = (to_id, 'friends') if to_id in friendship else (to_id, 'friend requests sent')
        else:
            friendship[from_id] = (from_id, 'friends') if from_id in friendship else (from_id, 'await your response')
    # get_name_from_id will update the internal cache so it will at most await once
    friends = {await get_name_from_id(user_id): status for user_id, status in friendship.values()}
    return TemplateResponse('home.html', {'request': request, 'filenames': user.filenames, 'name': user.name, 'friends': friends})

@login_required
async def create(request, user):
    if user.id == 0:
        return TemplateResponse('show.html', {'request': request, 'note': "Don't be a dick! Admin cannot create files!"})
    form = await request.form()
    data = await form['file'].read(4096)
    ext = 'txt'
    if '.' in form['file'].filename:
        _, _, ext = form['file'].filename.rpartition('.')
    if ext not in ('txt', 'png', 'html'):
        return TemplateResponse('show.html', {'request': request, 'note': "We only allow upload *.txt, *.png, *.html files!"})
    filename = rand() + '.' + ext
    async with aiofiles.open(UPLOAD_DIR / filename, 'wb') as f:
        await f.write(data)
    async with db.execute('INSERT INTO files (owner_id, filename) VALUES (?, ?)', (user.id, filename)) as cursor:
        await db.commit()
    request.session['filenames'].append(filename)
    return Redirect('home')

@login_required
async def view(request, user):
    filename = request.query_params.get('filename', '')
    async with db.execute('SELECT owner_id FROM files WHERE filename = ?', (filename, )) as cursor:
        row = await cursor.fetchone()
        owner_id, = (None, ) if row is None else row
    if owner_id is None:
        return TemplateResponse('show.html', {'request': request, 'note': 'No such file!'})
    if await is_friend(user.id, owner_id):
        return FileResponse(UPLOAD_DIR / filename)
    return TemplateResponse('show.html', {'request': request, 'note': "You need to be friends first to view other's files."})

@login_required
async def befriend(request, user):
    friend_name = request.query_params.get('friend_name', '')
    friend_id = await get_id_from_name(friend_name)
    if friend_id == user.id:
        return TemplateResponse('show.html', {'request': request, 'note': "You cannot be a friend of yourself...."})
    if friend_id is None:
        return TemplateResponse('show.html', {'request': request, 'note': "Oops.... your friend doesn't seem to exist."})
    async with db.execute('INSERT OR IGNORE INTO friendship (user_id, to_id) VALUES (?, ?)', (user.id, friend_id)):
        await db.commit()
    return Redirect('home')

@login_required
async def report(request, user):
    url = (await request.form()).get('url', '')
    if not (url.startswith('http://') or url.startswith('https://')):
        return TemplateResponse('show.html', {'request': request, 'note': "Invalud URL!"})
    queue.enqueue('xssbot.browse_all', [
        {
            'url': THIS_URL + 'admin_login',
            'timeout': 3,
        },
        {
            'url': url,
            'timeout': 5,
        }
    ])
    await asyncio.sleep(5)
    return TemplateResponse('show.html', {'request': request, 'note': 'Admin will check the link soon!'})

async def debug_user(request):
    if not request.session.get('debug', False):
        return TemplateResponse('show.html', {'request': request, 'note': 'Permission denied'})
    uid = request.query_params.get('id', request.session.get('id', -1))
    async with db.execute('SELECT user, pass FROM users WHERE id = ?', (uid, )) as cursor:
        row = await cursor.fetchone()
        user, pas = (None, None) if row is None else row
    return TemplateResponse('show.html', {
        'request': request,
        'pre': True,
        'note': f'''id : {uid}
name: {user}
pass: {pas}
'''
    })

async def exception_handler(request, exc):
    return TemplateResponse('show.html', {
        'request': request,
        'pre': True,
        'note':'\n'.join(['Internal Server Error:'] + [f'- {k}: {getattr(app, k)}' for k in app.__dir__()])
    }, status_code=500)

app = Starlette(
    debug=False,
    routes=[
        Route('/', endpoint=index, methods=['GET'], name='index'),
        Route('/login', endpoint=login, methods=['POST'], name='login'),
        Route('/admin_login', endpoint=admin_login, methods=['GET'], name='admin_login'),
        Route('/home', endpoint=home, methods=['GET'], name='home'),
        Route('/create', endpoint=create, methods=['POST'], name='create'),
        Route('/view', endpoint=view, methods=['GET'], name='view'),
        Route('/befriend', endpoint=befriend, methods=['GET'], name='befriend'),
        Route('/report', endpoint=report, methods=['POST'], name='report'),
        Route('/debug_user', endpoint=debug_user, methods=['GET'], name='debug_user'),
        # actually /static is delegated to nginx
        Mount('/static', StaticFiles(directory='static'), name='static')
    ],
    middleware=[
        # httponly is always enabled. The https_only here means "secure" flag in cookies
        # See source code:
        # https://github.com/encode/starlette/blob/8dac5c2c7c986121f57c6741f01b1df300eb5faa/starlette/middleware/sessions.py
        Middleware(SessionMiddleware, secret_key=SECRET_KEY, same_site='Strict', https_only=False),
    ],
    on_startup=[startup],
    on_shutdown=[shutdown],
    exception_handlers={
        HTTPException: exception_handler
    }
)

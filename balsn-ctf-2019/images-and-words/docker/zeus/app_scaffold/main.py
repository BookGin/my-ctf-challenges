#!/usr/bin/env python3
from pathlib import Path
import subprocess
import re
import secrets

from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.background import BackgroundTask
from starlette.staticfiles import StaticFiles

import config
import text2image

DEFAULT_RESPONSE = HTMLResponse('''
<h1>Images and Words</h1>
Convert text to a png file!
<form method="post" enctype="multipart/form-data">
    <input type="file" name="file">
    <input type="submit" value="Upload text" name="submit">
</form>
''')

server = Starlette(debug=config.DEBUG)
config.UPLOAD_DIR.mkdir(mode=0o700, exist_ok=True)
server.mount('/static', app=StaticFiles(directory=str(config.UPLOAD_DIR)))

def sanitize_filename(dangerous_filename):
    print(len(dangerous_filename))
    res = re.match(r'^[\.a-zA-Z0-9_-]([\.a-zA-Z0-9_-]+)*$', dangerous_filename)
    safe_filename = secrets.token_urlsafe(32)[:32] if res is None else dangerous_filename
    return safe_filename

def render(filename):
    src = config.UPLOAD_DIR / filename
    with open(src, 'r') as f:
        text = f.read()
    src.unlink()
    dst = config.UPLOAD_DIR / (filename + '.png')
    with open(dst, 'wb') as f:
        text2image.render(text, f)

@server.route('/', methods=['GET', 'POST'])
async def index(request):
    if request.method == 'POST':
        form = await request.form()
        if not form.get('file'):
            return DEFAULT_RESPONSE
        filename = sanitize_filename(form['file'].filename[:config.MAX_FILENAME_LEN])
        data = form['file'].file.read(config.MAX_TEXT_LEN)
        with open(config.UPLOAD_DIR / filename, 'wb') as f:
            f.write(data)
        return HTMLResponse(f'''
Your file will soon be available in <a href="static/{filename}.png">static/{filename}.png</a>
''', background=BackgroundTask(render, filename))
    return DEFAULT_RESPONSE

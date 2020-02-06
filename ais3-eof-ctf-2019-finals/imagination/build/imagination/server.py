#!/usr/bin/env python3
from flask import Flask, request, send_from_directory
from pathlib import Path

app = Flask(__name__)

@app.route('/<ftype>/<fname>', methods=['GET', 'POST'])
def index(ftype, fname):
    assert '.' not in ftype
    if request.method == 'GET':
        return send_from_directory(ftype, fname)
    str(p := Path(ftype)) in {'png_image', 'jpg_image', 'unknown_image'} and p.mkdir(exist_ok=True)
    return request.files['file'].save(str(p / fname)) or 'OK'

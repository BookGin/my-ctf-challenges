FROM python:3.9.1-buster

LABEL maintainer="bookgin"
LABEL description="Zero Storage Application"

RUN pip3 install --no-cache-dir redis rq
RUN pip3 install --no-cache-dir starlette python-multipart jinja2 uvloop httptools
RUN pip3 install --no-cache-dir uvicorn gunicorn aiosqlite aiofiles
RUN pip3 install --no-cache-dir itsdangerous

RUN apt update
RUN apt install -y --no-install-recommends nginx
RUN rm -rf /var/lib/apt/lists/*

RUN useradd --no-create-home --home-dir / --shell /bin/false user
CMD bash /run.sh

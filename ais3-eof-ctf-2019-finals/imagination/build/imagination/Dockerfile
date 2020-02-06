FROM python:3.8.1-slim

LABEL maintainer="bookgin"
LABEL version="1.0"
LABEL description="2020 EOF Final CTF Challenges - imagination"

RUN pip3 install --no-cache-dir gunicorn flask

# regular user
RUN useradd --create-home --shell /usr/sbin/nologin user
COPY server.py /home/user/server.py

# flag user
RUN useradd --no-create-home --home-dir / --shell /bin/false flag
COPY --chown=flag:flag flag/flag flag/readflag /
RUN chmod 400 /flag
RUN chmod 4755 /readflag

USER user
WORKDIR /home/user
EXPOSE 8000/TCP
CMD gunicorn \
    --workers 4 \
    --access-logfile - \
    --error-logfile - \
    --bind 0.0.0.0:8000 \
    server:app

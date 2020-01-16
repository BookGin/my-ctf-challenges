FROM python:alpine
LABEL maintainer="bookgin"

RUN apk add --no-cache build-base nginx sudo
RUN pip3 install --no-cache-dir starlette python-multipart 'databases[sqlite]' jinja2 gunicorn uvicorn
RUN adduser -s /sbin/nologin -D user
RUN mkdir -p /run/nginx

COPY nginx.conf /etc/nginx/nginx.conf
COPY *.py /home/user/

WORKDIR /home/user
CMD nginx && sudo -H -u user gunicorn \
    -k uvicorn.workers.UvicornWorker \
    --workers 8 \
    --access-logfile - \
    --error-logfile - \
    --bind=unix:./gunicorn.sock \
    server:app

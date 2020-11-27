FROM python:3.8.6-buster
# python@sha256:17d8f5c7909931f14eaf7c302c9b3b4ae7bc5bdd361f3c4a64145cd509e9180a

LABEL maintainer="bookgin"

RUN sed -i 's/deb.debian.org/debian.csie.ntu.edu.tw/g' /etc/apt/sources.list
RUN apt update -y

RUN apt install -y sudo
RUN apt install -y psmisc # pkill
RUN apt install -y nginx
RUN rm -rf /var/lib/apt/lists/*

RUN pip3 install starlette
RUN pip3 install uvicorn
RUN pip3 install gunicorn
RUN pip3 install python-multipart
RUN pip3 install itsdangerous
RUN pip3 install jinja2
RUN pip3 install uvloop
RUN pip3 install httptools

# flag will be moved at runtime
RUN mkdir /flag
COPY flag /flag/flag

# nginx
COPY default /etc/nginx/sites-available/default

# sandbox
RUN mkdir /sandbox
RUN chmod 733 /sandbox # drwx-wx-wx

CMD /app/run.sh

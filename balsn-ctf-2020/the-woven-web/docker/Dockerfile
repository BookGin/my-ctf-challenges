FROM debian:buster
# debian@sha256:8414aa82208bc4c2761dc149df67e25c6b8a9380e5d8c4e7b5c84ca2d04bb244

LABEL maintainer="bookgin"

#RUN sed -i 's/deb.debian.org/debian.csie.ntu.edu.tw/g' /etc/apt/sources.list
RUN apt update -y

RUN apt install -y chromium
RUN apt install -y chromium-driver
RUN apt install -y xvfb
RUN apt install -y redis-server
RUN apt install -y nodejs
RUN apt install -y npm
RUN apt install -y sudo
RUN apt install -y nginx
RUN rm -rf /var/lib/apt/lists/*

COPY --chown=redis:redis redis.conf /etc/redis/redis.conf
COPY default /etc/nginx/sites-available/default
RUN useradd --create-home --home-dir /home/user user
RUN mkdir /home/user/app

WORKDIR /home/user/app
RUN npm install redis 
RUN npm install express 
RUN npm install selenium-webdriver

CMD /home/user/app/run.sh

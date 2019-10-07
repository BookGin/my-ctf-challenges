FROM ubuntu:18.04
MAINTAINER bookgin

#RUN sed -i 's/archive\.ubuntu/tw.archive.ubuntu/g' /etc/apt/sources.list

RUN apt update -y
RUN apt upgrade -y

RUN apt install -y nginx
RUN apt install -y sudo
RUN apt install -y nmap # ncat
RUN apt install -y chromium-browser chromium-chromedriver
RUN apt install -y python3 python3-pip
RUN apt install -y redis-server
#RUN apt install -y psmisc # killall
RUN pip3 install \
  starlette \
  uvicorn \
  gunicorn \
  selenium \
  redis \
  rq

# flag
RUN useradd --no-create-home --home-dir / --shell /bin/false flag
COPY flag/flag /flag
COPY flag/readflag /readflag
RUN chown flag:flag /flag
RUN chown flag:flag /readflag
RUN chmod 400 /flag
RUN chmod 4755 /readflag

# other secure settings
RUN chmod 1733 /tmp /var/tmp #/dev/shm set this in runtime

# nginx
COPY nginx/default /etc/nginx/sites-available/default

# Redis
COPY --chown=redis:redis redis/redis.conf /etc/redis/redis.conf

# eval server
RUN useradd --no-create-home --home-dir / --shell /bin/false eval

# general user
COPY user /home/user
RUN useradd --no-create-home --home-dir /home/user --shell /bin/false user
# so user can access redis unix socket
RUN usermod --append -G redis user
# so www-data can read/write the unix socket
RUN usermod --append -G user www-data
RUN chown user:user /home/user/sock
RUN chown user:user /home/user/pow
RUN chmod 700 /home/user/pow
# Note: running python is almost the same as giving shell
RUN echo '\nuser ALL=(eval)NOPASSWD:/home/user/eval_server' >> /etc/sudoers

EXPOSE 80/tcp

WORKDIR /home/user
CMD bash run.sh

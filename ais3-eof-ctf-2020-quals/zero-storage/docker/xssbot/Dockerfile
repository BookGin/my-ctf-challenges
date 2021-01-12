FROM python:3.9.1-buster

LABEL maintainer="bookgin"
LABEL description="A redis-based Chromium XSS bot"

RUN sed -i 's/deb.debian.org/debian.csie.ntu.edu.tw/' /etc/apt/sources.list
RUN sed -i 's/security.debian.org/debian.csie.ntu.edu.tw/' /etc/apt/sources.list

RUN apt update
RUN apt install -y --no-install-recommends chromium-driver
RUN apt install -y --no-install-recommends redis-server
RUN apt install -y --no-install-recommends sudo
RUN apt install -y --no-install-recommends chromium
RUN rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir selenium redis rq

RUN useradd --no-create-home --home-dir / --shell /bin/false user
CMD bash /run.sh

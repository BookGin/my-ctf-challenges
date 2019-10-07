FROM ubuntu:18.04
MAINTAINER bookgin

#RUN sed -i 's/archive\.ubuntu/tw.archive.ubuntu/g' /etc/apt/sources.list

# system-wide config
RUN apt update -y
RUN apt upgrade -y
RUN chmod 1733 /tmp /var/tmp /dev/shm # Actually /dev/shm should be chmod on runtime

# Misc tools
RUN apt install -y nginx sudo python3 python3-pip psmisc
RUN pip3 install starlette uvicorn gunicorn pypng aiofiles python-multipart

# nginx
COPY nginx/default /etc/nginx/sites-available/default
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Create privileged scripts
COPY privileged-script/create_sandbox.sh /usr/bin/
COPY privileged-script/remove_sandbox.sh /usr/bin/
RUN chmod 755 /usr/bin/create_sandbox.sh
RUN chmod 755 /usr/bin/remove_sandbox.sh
RUN echo '\nzeus ALL=(root)NOPASSWD:/usr/bin/create_sandbox.sh *' >> /etc/sudoers
RUN echo '\nzeus ALL=(root)NOPASSWD:/usr/bin/remove_sandbox.sh *' >> /etc/sudoers

# flag
RUN useradd --no-create-home --home-dir / --shell /bin/false flag
COPY flag/flag /flag
COPY flag/readflag /readflag
RUN chown flag:flag /flag
RUN chown flag:flag /readflag
RUN chmod 400 /flag
RUN chmod 4755 /readflag

# Copy files and create user
COPY zeus /home/zeus
RUN useradd --no-create-home --home-dir /home/zeus --shell /bin/false zeus
RUN usermod --append -G zeus www-data
RUN chmod 711 /home/zeus/sandbox
RUN chown zeus:zeus /home/zeus/sock
RUN chown zeus:zeus /home/zeus/pow
RUN chmod 700 /home/zeus/pow

EXPOSE 80/tcp
CMD bash /home/zeus/run.sh

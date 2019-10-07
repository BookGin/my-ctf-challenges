#!/usr/bin/env bash

chmod 1733 /dev/shm

# Start redis
service redis-server restart

# Start redis worker
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
for _ in {1..4}; do
  sudo -H -u user rq worker --url 'unix:///var/run/redis/redis-server.sock' &
done

# Start eval_server
sudo -H -u user ncat -klv 127.0.0.1 6666 -c 'timeout 30 sudo -H -u eval ./eval_server' &

# Start nginx
service nginx restart

# Start web server
sudo -H -u user gunicorn \
  --bind unix:sock/server.sock \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers 5 \
  --access-logfile - \
  --error-logfile - \
  --umask 007 \
  web_server:app
